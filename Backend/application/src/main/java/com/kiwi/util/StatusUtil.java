package com.kiwi.util;

public class StatusUtil {

    public static String toApiStatus(Integer status) {
        return switch (status) {
            case 0 -> "pending";
            case 1 -> "processing";
            case 2 -> "done";
            case 3 -> "failed";
            default -> "unknown";
        };
    }

}
