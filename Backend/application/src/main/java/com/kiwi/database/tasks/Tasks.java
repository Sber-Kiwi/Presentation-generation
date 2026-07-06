package com.kiwi.database.tasks;

import com.kiwi.database.chat.Chats;
import com.kiwi.database.slides.Slides;
import com.kiwi.database.versions.Versions;
import jakarta.persistence.*;

import java.util.Objects;

@Entity
public class Tasks {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer taskID;
    private Integer type;
    private String prompt;
    private Integer status;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "chatID")
    private Chats chat;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "versionID", nullable = true)
    private Versions version;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "slideID", nullable = true)
    private Slides slide;

    public Integer getTaskID() {
        return taskID;
    }

    public void setTaskID(Integer taskID) {
        this.taskID = taskID;
    }

    public Integer getType() {
        return type;
    }

    public void setType(Integer type) {
        this.type = type;
    }

    public String getPrompt() {
        return prompt;
    }

    public void setPrompt(String prompt) {
        this.prompt = prompt;
    }

    public Integer getStatus() {
        return status;
    }

    public void setStatus(Integer status) {
        this.status = status;
    }

    public Chats getChat() {
        return chat;
    }

    public void setChat(Chats chat) {
        this.chat = chat;
    }

    public Versions getVersion() {
        return version;
    }

    public void setVersion(Versions version) {
        this.version = version;
    }

    @Override
    public boolean equals(Object o) {
        if (o == null || getClass() != o.getClass()) return false;
        Tasks tasks = (Tasks) o;
        return Objects.equals(taskID, tasks.taskID) && Objects.equals(type, tasks.type) && Objects.equals(prompt, tasks.prompt) && Objects.equals(status, tasks.status) && Objects.equals(chat, tasks.chat) && Objects.equals(version, tasks.version);
    }

    @Override
    public int hashCode() {
        return Objects.hash(taskID, type, prompt, status, chat, version);
    }
}
