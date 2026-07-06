package com.kiwi.database.versions;

import org.springframework.data.jpa.repository.JpaRepository;

public interface VersionsRepository extends JpaRepository<Versions, Integer> {
}
