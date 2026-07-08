package com.kiwi.dto.request;

import jakarta.validation.constraints.NotNull;

public class SlideStateDto {

    @NotNull
    private String slideID;

    @NotNull
    private String selectedVersionID;

    @NotNull
    private Boolean inPresentation;

    public String getSlideID() {
        return slideID;
    }

    public void setSlideID(String slideID) {
        this.slideID = slideID;
    }

    public String getSelectedVersionID() {
        return selectedVersionID;
    }

    public void setSelectedVersionID(String selectedVersionID) {
        this.selectedVersionID = selectedVersionID;
    }

    public Boolean getInPresentation() {
        return inPresentation;
    }

    public void setInPresentation(Boolean inPresentation) {
        this.inPresentation = inPresentation;
    }
}
