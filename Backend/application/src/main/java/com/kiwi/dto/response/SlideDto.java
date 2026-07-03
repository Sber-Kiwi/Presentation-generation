package com.kiwi.dto.response;

import com.kiwi.dto.request.SlideStateDto;
import com.kiwi.dto.request.SlideVersionDto;

import java.util.List;

public class SlideDto {

    private String slideID;

    private Integer order;

    private List<SlideVersionDto> versions;

    private SlideStateDto state;

    public String getSlideID() {
        return slideID;
    }

    public void setSlideID(String slideID) {
        this.slideID = slideID;
    }

    public Integer getOrder() {
        return order;
    }

    public void setOrder(Integer order) {
        this.order = order;
    }

    public List<SlideVersionDto> getVersions() {
        return versions;
    }

    public void setVersions(List<SlideVersionDto> versions) {
        this.versions = versions;
    }

    public SlideStateDto getState() {
        return state;
    }

    public void setState(SlideStateDto state) {
        this.state = state;
    }
}
