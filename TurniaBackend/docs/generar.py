#!/usr/bin/env python3
"""Genera el catálogo de obras sociales de Argentina para el Central (msvc-salud).

Uso (desde la raíz del repo):  python3 docs/obras-sociales/generar.py [copia_rnos.html]

- Obras sociales nacionales: Registro Nacional de Obras Sociales (RNOS) de la Superintendencia de Servicios
  de Salud (https://www.sssalud.gob.ar/index.php?page=listRnosc&cat=consultas&tipo=1), con código RNAS.
- PAMI, IOSFA, OSPJN, obras sociales provinciales, prepagas y programas (SUMAR, Incluir Salud): no están en
  ese registro, se cargan a mano acá (revisar y completar desde el panel del superadmin).
Los primeros IDs quedan fijos: 1 = Sin obra social, 2 = PAMI, 3 = Programa SUMAR.
"""
import codecs
import html
import pathlib
import re
import sys
import unicodedata
import urllib.request

# La página es UTF-8 pero trae algún byte suelto en Latin-1 (ej. la Ñ de OSPAÑA)
codecs.register_error("latin1_suelto", lambda e: (e.object[e.start:e.end].decode("latin-1"), e.end))

# Errores de tipeo del registro original
CORRECCIONES = {"Administraci Ón": "Administración", "Descendiente S ": "Descendientes "}

RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
DESTINO = RAIZ / "anda-central/msvc-salud/src/main/resources/db/migration/V3_1__obras_sociales.sql"
URL_RNOS = "https://www.sssalud.gob.ar/index.php?page=listRnosc&cat=consultas&tipo=1"

# (nombre, sigla, tipo, deriva_accion_social)
FIJAS = [
    ("Sin obra social", "SIN OS", "SIN_COBERTURA", True),
    ("PAMI - Instituto Nacional de Servicios Sociales para Jubilados y Pensionados", "PAMI", "NACIONAL", False),
    ("Programa SUMAR (sin cobertura)", "SUMAR", "PROGRAMA", True),
    ("Programa Incluir Salud (ex PROFE)", "INCLUIR SALUD", "PROGRAMA", False),
    ("IOSFA - Instituto de Obra Social de las Fuerzas Armadas y de Seguridad", "IOSFA", "NACIONAL", False),
    ("Obra Social del Poder Judicial de la Nación", "OSPJN", "NACIONAL", False),
]
PROVINCIALES = [
    ("IOMA - Instituto de Obra Médico Asistencial (Buenos Aires)", "IOMA"),
    ("ObSBA - Obra Social de la Ciudad de Buenos Aires", "OBSBA"),
    ("OSEP - Obra Social de los Empleados Públicos (Catamarca)", "OSEP CATAMARCA"),
    ("INSSSEP - Instituto de Seguridad Social, Seguros y Préstamos (Chaco)", "INSSSEP"),
    ("SEROS - Instituto de Seguridad Social y Seguros (Chubut)", "SEROS"),
    ("APROSS - Administración Provincial del Seguro de Salud (Córdoba)", "APROSS"),
    ("IOSCOR - Instituto de Obra Social de Corrientes", "IOSCOR"),
    ("OSER - Obra Social de Entre Ríos (ex IOSPER)", "OSER"),
    ("IASEP - Instituto de Asistencia Social para Empleados Públicos (Formosa)", "IASEP"),
    ("ISJ - Instituto de Seguros de Jujuy", "ISJ"),
    ("SEMPRE - Servicio Médico Integral para Empleados (La Pampa)", "SEMPRE"),
    ("APOS - Administración Provincial de Obra Social (La Rioja)", "APOS"),
    ("OSEP - Obra Social de Empleados Públicos (Mendoza)", "OSEP MENDOZA"),
    ("IPS Misiones - Instituto de Previsión Social", "IPS MISIONES"),
    ("ISSN - Instituto de Seguridad Social del Neuquén", "ISSN"),
    ("IPROSS - Instituto Provincial del Seguro de Salud (Río Negro)", "IPROSS"),
    ("IPS Salta - Instituto Provincial de Salud de Salta", "IPS SALTA"),
    ("Obra Social Provincia de San Juan", "OSP SAN JUAN"),
    ("DOSEP - Dirección de Obra Social del Estado Provincial (San Luis)", "DOSEP"),
    ("CSS - Caja de Servicios Sociales (Santa Cruz)", "CSS"),
    ("IAPOS - Instituto Autárquico Provincial de Obra Social (Santa Fe)", "IAPOS"),
    ("IOSEP - Instituto de Obra Social del Empleado Provincial (Santiago del Estero)", "IOSEP"),
    ("OSEF - Obra Social del Estado Fueguino (Tierra del Fuego)", "OSEF"),
    ("Subsidio de Salud - Instituto de Previsión y Seguridad Social de Tucumán", "SUBSIDIO DE SALUD"),
]
PREPAGAS = [
    ("Swiss Medical", "SWISS"), ("Galeno", "GALENO"), ("Medifé", "MEDIFE"), ("Sancor Salud", "SANCOR"),
    ("OMINT", "OMINT"), ("Medicus", "MEDICUS"), ("Hospital Italiano - Plan de Salud", "HIBA"),
    ("Hospital Alemán - Plan Médico", "HOSPITAL ALEMAN"), ("Hospital Británico - Plan de Salud", "HOSPITAL BRITANICO"),
    ("Accord Salud", "ACCORD"), ("Avalian", "AVALIAN"), ("Prevención Salud", "PREVENCION"),
    ("Federada Salud", "FEDERADA"), ("Jerárquicos Salud", "JERARQUICOS"), ("Premedic", "PREMEDIC"),
    ("Sanatorio Güemes - Plan de Salud", "GUEMES"), ("Doctored", "DOCTORED"), ("Bristol Medicine", "BRISTOL"),
]


def busqueda(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


def sql(s):
    return "NULL" if s is None else "'" + s.replace("'", "''") + "'"


def titulo(nombre):
    """El registro viene en mayúsculas: se pasa a formato título conservando siglas cortas."""
    chicas = {"de", "del", "la", "las", "los", "y", "e", "el", "en", "a", "para", "por"}
    palabras = nombre.lower().split()
    t = " ".join(p if (i > 0 and p in chicas) else p.capitalize() for i, p in enumerate(palabras))
    t = re.sub(r"\bS\.a\.?(?=\s|$)", "S.A.", re.sub(r"\bS\.r\.l\.?(?=\s|$)", "S.R.L.", t))
    for mal, bien in CORRECCIONES.items():
        t = t.replace(mal, bien)
    return t


# El sitio responde 403 sin un User-Agent de navegador. Con un argumento se usa una copia guardada.
if len(sys.argv) > 1:
    pagina = pathlib.Path(sys.argv[1]).read_bytes().decode("utf-8", errors="latin1_suelto")
else:
    pedido = urllib.request.Request(URL_RNOS, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/126"})
    with urllib.request.urlopen(pedido, timeout=120) as r:
        pagina = r.read().decode("utf-8", errors="latin1_suelto")
rnos = []
for fila in re.findall(r"<tr[^>]*>(.*?)</tr>", pagina, re.S | re.I)[1:]:
    celdas = [html.unescape(re.sub("<[^>]+>", "", c)).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", fila, re.S | re.I)]
    if len(celdas) >= 3 and re.match(r"\d-\d{4}-\d", celdas[0]):
        rnos.append((celdas[0], re.sub(r"\s+", " ", celdas[1]), celdas[2] or None))
assert len(rnos) > 300, len(rnos)

filas, vistos = [], set()


def agregar(nombre, sigla, tipo, rnas=None, deriva=False):
    clave = busqueda(nombre)
    if clave in vistos:
        nombre = f"{nombre} ({rnas or sigla})"
        clave = busqueda(nombre)
    vistos.add(clave)
    filas.append(f"({len(filas) + 1},{sql(nombre)},{sql(sigla)},{sql(tipo)},{sql(rnas)},"
                 f"{'TRUE' if deriva else 'FALSE'},{sql(busqueda(nombre + ' ' + (sigla or '')).strip())})")


for n, s, t, d in FIJAS:
    agregar(n, s, t, deriva=d)
for n, s in PROVINCIALES:
    agregar(n, s, "PROVINCIAL")
for rnas, n, s in sorted(rnos, key=lambda x: busqueda(x[1])):
    agregar(titulo(n), s, "PREPAGA" if rnas.startswith("9-") else "NACIONAL", rnas)
# Varias prepagas ya figuran en el RNOS como entidades adheridas (códigos 9-xxxx): no se duplican
nombres_rnos = [busqueda(n) for _, n, _ in rnos]
for n, s in PREPAGAS:
    if not any(n_rnos.startswith(busqueda(n)) for n_rnos in nombres_rnos):
        agregar(n, s, "PREPAGA")

DESTINO.write_text(f"""-- Obras sociales de Argentina: {len(rnos)} del Registro Nacional de Obras Sociales (Superintendencia de
-- Servicios de Salud, con código RNAS), más PAMI, IOSFA, OSPJN, las provinciales, prepagas y programas (SUMAR,
-- Incluir Salud) cargadas a mano. Generado por docs/obras-sociales/generar.py.
-- deriva_accion_social: sin cobertura → Programa SUMAR → Acción Social de la ciudad.

INSERT INTO obras_sociales (id, nombre, sigla, tipo, codigo_rnas, deriva_accion_social, busqueda) VALUES
{",\n".join(filas)};

SELECT setval(pg_get_serial_sequence('obras_sociales', 'id'), (SELECT MAX(id) FROM obras_sociales));
""", encoding="utf-8")
print(len(filas), "obras sociales →", DESTINO.relative_to(RAIZ))
