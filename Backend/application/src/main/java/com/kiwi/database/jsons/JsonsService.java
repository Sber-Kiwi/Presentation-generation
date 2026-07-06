package com.kiwi.database.jsons;

import jakarta.persistence.EntityNotFoundException;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class JsonsService {
    private final JsonsRepository jsonsRepository;

    public JsonsService(JsonsRepository jsonsRepository) { this.jsonsRepository = jsonsRepository; }

    public List<Jsons> getAllJsons() { return jsonsRepository.findAll(); }

    public Jsons getJsonById(Integer jsonId) {
        return jsonsRepository.findById(jsonId).orElseThrow(() -> new EntityNotFoundException("Json not found " + jsonId));
    }

    public void addJson(Jsons json) { jsonsRepository.save(json); }

    public Jsons updateJson(Integer jsonId, Jsons updatedJson) {
        Jsons exsisting = getJsonById(jsonId);
        exsisting.setFile(updatedJson.getFile());
        return jsonsRepository.save(exsisting);
    }

    public void deleteJson(Integer jsonId) {
        if(!jsonsRepository.existsById(jsonId)) {
            throw new EntityNotFoundException("Json not found " + jsonId);
        }
        jsonsRepository.deleteById(jsonId);
    }
}
