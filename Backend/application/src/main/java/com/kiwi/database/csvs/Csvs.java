package com.kiwi.database.csvs;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.kiwi.database.chat.Chats;
import jakarta.persistence.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.util.Arrays;
import java.util.Objects;

@Entity
public class Csvs {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer csvID;

    @Column(name = "file", columnDefinition = "BYTEA")
    @JdbcTypeCode(SqlTypes.VARBINARY)
    private byte[] file;

    public Integer getCsvID() {
        return csvID;
    }

    public void setCsvID(Integer csvID) {
        this.csvID = csvID;
    }

    public byte[] getFile() {
        return file;
    }

    public void setFile(byte[] file) {
        this.file = file;
    }

    @Override
    public boolean equals(Object o) {
        if (o == null || getClass() != o.getClass()) return false;
        Csvs csvs = (Csvs) o;
        return Objects.equals(csvID, csvs.csvID) && Objects.deepEquals(file, csvs.file);
    }

    @Override
    public int hashCode() {
        return Objects.hash(csvID, Arrays.hashCode(file));
    }
}