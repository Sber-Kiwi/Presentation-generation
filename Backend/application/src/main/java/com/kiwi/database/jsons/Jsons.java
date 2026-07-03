package com.kiwi.database.jsons;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.kiwi.database.chat.Chats;
import jakarta.persistence.*;

import java.util.Objects;

@Entity
public class Jsons {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer jsonID;

    @Column(columnDefinition = "jsonb")
    private String file;

    @OneToOne(mappedBy = "json", cascade = CascadeType.ALL)
    @JsonIgnore
    private Chats chat;

    public Integer getJsonID() {
        return jsonID;
    }

    public void setJsonID(Integer jsonID) {
        this.jsonID = jsonID;
    }

    public String getFile() {
        return file;
    }

    public void setFile(String file) {
        this.file = file;
    }

    public Chats getChat() {
        return chat;
    }

    public void setChat(Chats chat) {
        this.chat = chat;
    }

    @Override
    public boolean equals(Object o) {
        if (o == null || getClass() != o.getClass()) return false;
        Jsons jsons = (Jsons) o;
        return Objects.equals(jsonID, jsons.jsonID) && Objects.equals(file, jsons.file) && Objects.equals(chat, jsons.chat);
    }

    @Override
    public int hashCode() {
        return Objects.hash(jsonID, file, chat);
    }
}
