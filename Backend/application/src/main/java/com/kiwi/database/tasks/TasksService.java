package com.kiwi.database.tasks;

import org.springframework.stereotype.Service;

@Service
public class TasksService {

    private final TasksRepository tasksRepository;

    public TasksService(TasksRepository tasksRepository) {
        this.tasksRepository = tasksRepository;
    }

    @org.springframework.transaction.annotation.Transactional(propagation = org.springframework.transaction.annotation.Propagation.REQUIRES_NEW)
    public void updateTaskStatus(Integer taskId, int status) {
        Tasks task = tasksRepository.findById(taskId).orElse(null);
        if (task != null) {
            task.setStatus(status);
            tasksRepository.save(task);
        }
    }

}
