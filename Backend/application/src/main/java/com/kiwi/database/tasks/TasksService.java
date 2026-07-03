package com.kiwi.database.tasks;

import org.springframework.stereotype.Service;

@Service
public class TasksService {

    private final TasksRepository tasksRepository;

    public TasksService(TasksRepository tasksRepository) {
        this.tasksRepository = tasksRepository;
    }

}
