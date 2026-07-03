package com.kiwi.dto.response;

public class SlideStatusDto {

    private String status;
    private String newVersionID;
    private String error;

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getNewVersionID() {
        return newVersionID;
    }

    public void setNewVersionID(String newVersionID) {
        this.newVersionID = newVersionID;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}
