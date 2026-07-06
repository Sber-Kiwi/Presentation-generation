package com.kiwi.database.csvs;

import jakarta.persistence.EntityNotFoundException;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class CsvsService {

    private final CsvsRepository csvsRepository;

    public CsvsService(CsvsRepository csvsRepository) {
        this.csvsRepository = csvsRepository;
    }

    public List<Csvs> getAllCsvs() {return csvsRepository.findAll(); }

    public Csvs getCsvById (Integer csvId) {
        return csvsRepository.findById(csvId).orElseThrow(() -> new EntityNotFoundException("Csv not found " + csvId));
    }

    public void addCsv(Csvs csv) {
        csvsRepository.save(csv);
    }

    public void deleteCsv(Integer csvId) {
        if(!csvsRepository.existsById(csvId)) {
            throw new EntityNotFoundException("Csv not found " + csvId);
        }
    }
}
