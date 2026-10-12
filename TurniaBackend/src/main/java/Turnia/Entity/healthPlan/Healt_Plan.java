package Turnia.Entity.healthPlan;

import java.time.LocalDateTime;

public class Healt_Plan {
    
    private Long id_plan;
    private String name_plan;
    private Long number_plan;
    private LocalDateTime  start_date_plan;
    public Healt_Plan() {
    }
    public Healt_Plan(Long id_plan, String name_plan, Long number_plan, LocalDateTime start_date_plan) {
        this.id_plan = id_plan;
        this.name_plan = name_plan;
        this.number_plan = number_plan;
        this.start_date_plan = start_date_plan;
    }
    public Long getId_plan() {
        return id_plan;
    }
    public void setId_plan(Long id_plan) {
        this.id_plan = id_plan;
    }
    public String getName_plan() {
        return name_plan;
    }
    public void setName_plan(String name_plan) {
        this.name_plan = name_plan;
    }
    public Long getNumber_plan() {
        return number_plan;
    }
    public void setNumber_plan(Long number_plan) {
        this.number_plan = number_plan;
    }
    public LocalDateTime getStart_date_plan() {
        return start_date_plan;
    }
    public void setStart_date_plan(LocalDateTime start_date_plan) {
        this.start_date_plan = start_date_plan;
    }
    
}
