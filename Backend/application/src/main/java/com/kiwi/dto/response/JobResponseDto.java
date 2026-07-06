package com.kiwi.dto.response;

public class JobResponseDto {

    private String chatID;
    private String slideID;
    private String status;
    private String taskID;

    public String getChatID() {
        return chatID;
    }

    public void setChatID(String chatID) {
        this.chatID = chatID;
    }

    public String getSlideID() {
        return slideID;
    }

    public void setSlideID(String slideID) {
        this.slideID = slideID;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getTaskID() {
        return taskID;
    }

    public void setTaskID(String taskID) {
        this.taskID = taskID;
    }
}
