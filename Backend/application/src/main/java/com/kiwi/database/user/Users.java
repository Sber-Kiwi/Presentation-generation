package com.kiwi.database.user;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.kiwi.database.chat.Chats;
import jakarta.persistence.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

@Entity
public class Users {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer userID;
    private String department;

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonIgnore
    private List<Chats> chats = new ArrayList<>();

    public Integer getUserid() {
        return userID;
    }

    public void setUserid(Integer userid) {
        this.userID = userid;
    }

    public String getDepartment() {
        return department;
    }

    public void setDepartment(String department) {
        this.department = department;
    }

    public List<Chats> getChats() {
        return chats;
    }

    public void setChats(List<Chats> chats) {
        this.chats = chats;
    }

    @Override
    public boolean equals(Object o) {
        if (o == null || getClass() != o.getClass()) return false;
        Users users = (Users) o;
        return Objects.equals(userID, users.userID) && Objects.equals(department, users.department) && Objects.equals(chats, users.chats);
    }

    @Override
    public int hashCode() {
        return Objects.hash(userID, department, chats);
    }
}
