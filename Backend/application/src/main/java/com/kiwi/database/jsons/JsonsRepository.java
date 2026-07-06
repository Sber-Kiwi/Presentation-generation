package com.kiwi.database.jsons;

import com.kiwi.database.jsons.Jsons;
import org.springframework.data.jpa.repository.JpaRepository;

public interface JsonsRepository extends JpaRepository<Jsons, Integer> {
}