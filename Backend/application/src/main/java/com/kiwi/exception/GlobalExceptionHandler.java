package com.kiwi.exception;

import com.kiwi.dto.response.ErrorDto;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;

import java.util.List;

public class GlobalExceptionHandler {

    @ExceptionHandler(NotFoundException.class)
    public ResponseEntity<ErrorDto> handleNotFoundException(NotFoundException e) {
        return ResponseEntity.status(404).body(new ErrorDto("NOT_FOUND", e.getMessage()));
    }

    @ExceptionHandler(ValidationException.class)
    public ResponseEntity<ErrorDto> handleValidationException(ValidationException e) {
        return ResponseEntity.status(422).body(new ErrorDto("VALIDATION_ERROR", e.getMessage()));
    }

    @ExceptionHandler(ConflictException.class)
    public ResponseEntity<ErrorDto> handleConflictException(ConflictException e) {
        return ResponseEntity.status(409).body(new ErrorDto("CONFLICT", e.getMessage()));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorDto> handleMethodArgumentNotValidException(MethodArgumentNotValidException e) {
        List<ErrorDto.FieldError> details = e.getBindingResult()
                .getFieldErrors().stream()
                .map(ex -> new ErrorDto.FieldError(ex.getField(), ex.getDefaultMessage()))
                .toList();
        return ResponseEntity.status(422).body(new ErrorDto("VALIDATION_ERROR", "Validation failed", details));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorDto> handleException(Exception e) {
        return ResponseEntity.status(500).body(new ErrorDto("INTERNAL_SERVER_ERROR", e.getMessage()));
    }

}
