package com.kiwi.database.chat;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.kiwi.database.csvs.Csvs;
import com.kiwi.database.jsons.Jsons;
import com.kiwi.database.slides.Slides;
import com.kiwi.database.tasks.Tasks;
import com.kiwi.database.user.Users;
import jakarta.persistence.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

@Entity
public class Chats {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer chatID;
    private String title;
    private String prompt;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "userID",  nullable = false)
    private Users user;

    @OneToOne(fetch = FetchType.LAZY, cascade = CascadeType.PERSIST)
    @JoinColumn(name = "csvID", unique = true, nullable = false)
    private Csvs csv;

    @OneToOne
    @JoinColumn(name = "jsonID", unique = true)
    private Jsons json;

    @OneToMany(mappedBy = "chat", cascade = CascadeType.ALL)
    @JsonIgnore
    private List<Tasks> tasks = new ArrayList<>();

    @OneToMany(mappedBy = "chat", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonIgnore
    private List<Slides> slides = new ArrayList<>();

    public Integer getChatID() {
        return chatID;
    }

    public void setChatID(Integer chatID) {
        this.chatID = chatID;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getPrompt() {
        return prompt;
    }

    public void setPrompt(String prompt) {
        this.prompt = prompt;
    }

    public Users getUser() {
        return user;
    }

    public void setUser(Users user) {
        this.user = user;
    }

    public Csvs getCsv() {
        return csv;
    }

    public void setCsv(Csvs csv) {
        this.csv = csv;
    }

    public Jsons getJson() {
        return json;
    }

    public void setJson(Jsons json) {
        this.json = json;
    }

    public List<Tasks> getTasks() {
        return tasks;
    }

    public void setTasks(List<Tasks> tasks) {
        this.tasks = tasks;
    }

    public List<Slides> getSlides() {
        return slides;
    }

    public void setSlides(List<Slides> slides) {
        this.slides = slides;
    }

    @Override
    public boolean equals(Object o) {
        if (o == null || getClass() != o.getClass()) return false;
        Chats chats = (Chats) o;
        return Objects.equals(chatID, chats.chatID) && Objects.equals(title, chats.title) && Objects.equals(prompt, chats.prompt) && Objects.equals(user, chats.user) && Objects.equals(csv, chats.csv) && Objects.equals(json, chats.json) && Objects.equals(tasks, chats.tasks) && Objects.equals(slides, chats.slides);
    }

    @Override
    public int hashCode() {
        return Objects.hash(chatID, title, prompt, user, csv, json, tasks, slides);
    }
}