package Turnia.Entity.userEntity;

import java.time.LocalDateTime;

import Turnia.Entity.healthPlan.Healt_Plan;



public class user {
    
    private Long id;
    private String name;
    private String lastName;
    private String DNI;
    private String phone;
    private boolean isctive = true;
    private LocalDateTime upDate;
    private Healt_Plan userHealtPlan;
    public user() {
    }
    public user(Long id, String name, String lastName, String dNI, String phone, Healt_Plan user_Plan) {
        this.id = id;
        this.name = name;
        this.lastName = lastName;
        DNI = dNI;
        this.phone = phone;
        this.isctive = true;
        this.upDate = LocalDateTime.now() ;
        this.userHealtPlan = user_Plan;
    }
    public Long getId() {
        return id;
    }
    public void setId(Long id) {
        this.id = id;
    }
    public String getName() {
        return name;
    }
    public void setName(String name) {
        this.name = name;
    }
    public String getLastName() {
        return lastName;
    }
    public void setLastName(String lastName) {
        this.lastName = lastName;
    }
    public String getDNI() {
        return DNI;
    }
    public void setDNI(String dNI) {
        DNI = dNI;
    }
    public String getPhone() {
        return phone;
    }
    public void setPhone(String phone) {
        this.phone = phone;
    }
    public boolean isIsctive() {
        return isctive;
    }
    public void setIsctive(boolean isctive) {
        this.isctive = isctive;
    }
    public LocalDateTime getUpDate() {
        return upDate;
    }
    public void setUpDate(LocalDateTime upDate) {
        this.upDate = upDate;
    }
    public Healt_Plan getUserHealtPlan() {
        return userHealtPlan;
    }
    public void setUserHealtPlan(Healt_Plan userHealtPlan) {
        this.userHealtPlan = userHealtPlan;
    }
    
    
    
}
