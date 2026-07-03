package com.kiwi.database.versions;

import com.kiwi.database.slides.Slides;
import jakarta.persistence.*;

import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

@Entity
public class Versions {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer versionID;
    private String prompt;
    private Boolean isFinal;

    @Column(columnDefinition = "jsonb")
    private String json;

    @Column(columnDefinition = "TIMESTAMP WITH TIME ZONE", nullable = false)
    private OffsetDateTime createdAt;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "slideID", nullable = false)
    private Slides slide;

    public Integer getVersionID() {
        return versionID;
    }

    public void setVersionID(Integer versionID) {
        this.versionID = versionID;
    }

    public String getPrompt() {
        return prompt;
    }

    public void setPrompt(String prompt) {
        this.prompt = prompt;
    }

    public Boolean getFinal() {
        return isFinal;
    }

    public void setFinal(Boolean aFinal) {
        isFinal = aFinal;
    }

    public String getJson() {
        return json;
    }

    public void setJson(String json) {
        this.json = json;
    }

    public OffsetDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(OffsetDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public Slides getSlide() {
        return slide;
    }

    public void setSlide(Slides slide) {
        this.slide = slide;
    }

    @Override
    public boolean equals(Object o) {
        if (o == null || getClass() != o.getClass()) return false;
        Versions versions = (Versions) o;
        return Objects.equals(versionID, versions.versionID) && Objects.equals(prompt, versions.prompt) && Objects.equals(isFinal, versions.isFinal) && Objects.equals(json, versions.json) && Objects.equals(createdAt, versions.createdAt) && Objects.equals(slide, versions.slide);
    }

    @Override
    public int hashCode() {
        return Objects.hash(versionID, prompt, isFinal, json, createdAt, slide);
    }
}