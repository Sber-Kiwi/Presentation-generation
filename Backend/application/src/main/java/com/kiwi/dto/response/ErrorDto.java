package com.kiwi.dto.response;

import java.util.List;

public class ErrorDto {

    private String code;
    private String message;
    private List<FieldError> details;

    public static class FieldError {
        private String field;
        private String message;

        public FieldError(String field, String message) {
            this.field = field;
            this.message = message;
        }

        public String getField() {
            return field;
        }

        public String getMessage() {
            return message;
        }
    }

    public ErrorDto(String code, String message) {
        this.code = code;
        this.message = message;
    }

    public ErrorDto(String code, String message, List<FieldError> details) {
        this.code = code;
        this.message = message;
        this.details = details;
    }

    public String getCode() {
        return code;
    }

    public String getMessage() {
        return message;
    }

    public List<FieldError> getDetails() {
        return details;
    }
}
