package com.kiwi.database.csvs;

import com.kiwi.database.chat.ChatsRepository;
import org.springframework.stereotype.Service;

@Service
public class CsvsService {

    private CsvsRepository csvsRepository;

    public CsvsService(CsvsRepository csvsRepository) {
        this.csvsRepository = csvsRepository;
    }

    public void addScv(Csvs csv) {
        csvsRepository.save(csv);
    }

}
