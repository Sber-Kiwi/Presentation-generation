package com.kiwi.database.tasks;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface TasksRepository extends JpaRepository<Tasks, Integer> {

    Optional<Tasks> findTopByChat_ChatIDAndTypeOrderByTaskIDDesc(Integer chatID, Integer type);

    List<Tasks> findByStatusIn(List<Integer> statuses);

}