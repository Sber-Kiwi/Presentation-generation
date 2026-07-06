package com.kiwi.util;

public class IdUtil {

    public static String chatId(Integer id) {
        return "chat_" + id;
    }

    public static String slideId(Integer id) {
        return "slide_" + id;
    }

    public static String versionId(Integer id) {
        return "version_" + id;
    }

    public static String taskId(Integer id) {
        return "task_" + id;
    }

    public static Integer parseChatId (String id) {
        return Integer.valueOf(id.replace("chat_", ""));
    }

    public static Integer parseSlideId(String id) {
        return Integer.valueOf(id.replace("slide_", ""));
    }

    public static Integer parseVersionId(String id) {
        return Integer.valueOf(id.replace("version_", ""));
    }

    public static Integer parseTaskId(String id) {
        return Integer.valueOf(id.replace("task_", ""));
    }


}
