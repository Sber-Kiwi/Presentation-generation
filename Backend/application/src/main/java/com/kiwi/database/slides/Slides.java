package com.kiwi.database.slides;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.kiwi.database.chat.Chats;
import com.kiwi.database.versions.Versions;
import jakarta.persistence.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

@Entity
public class Slides {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer slideID;
    private Short num;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "chatID", nullable = false)
    private Chats chat;

    @OneToMany(mappedBy = "slide", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonIgnore
    private List<Versions> versions = new ArrayList<>();

    public Integer getSlideID() {
        return slideID;
    }

    public void setSlideID(Integer slideID) {
        this.slideID = slideID;
    }

    public Short getNum() {
        return num;
    }

    public void setNum(Short num) {
        this.num = num;
    }

    public Chats getChat() {
        return chat;
    }

    public void setChat(Chats chat) {
        this.chat = chat;
    }

    public List<Versions> getVersions() {
        return versions;
    }

    public void setVersions(List<Versions> versions) {
        this.versions = versions;
    }

    @Override
    public boolean equals(Object o) {
        if (o == null || getClass() != o.getClass()) return false;
        Slides slides = (Slides) o;
        return Objects.equals(slideID, slides.slideID) && Objects.equals(num, slides.num) && Objects.equals(chat, slides.chat) && Objects.equals(versions, slides.versions);
    }

    @Override
    public int hashCode() {
        return Objects.hash(slideID, num, chat, versions);
    }
}