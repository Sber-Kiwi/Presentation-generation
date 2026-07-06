package com.kiwi.database.slides;

import com.kiwi.database.chat.Chats;
import com.kiwi.database.chat.ChatsRepository;
import jakarta.persistence.EntityNotFoundException;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.util.List;

@Service
public class SlidesService {
    private final SlidesRepository slidesRepository;
    private final ChatsRepository chatsRepository;

    public SlidesService(SlidesRepository slidesRepository, ChatsRepository chatsRepository) {
        this.slidesRepository = slidesRepository;
        this.chatsRepository = chatsRepository;
    }

    public List<Slides> getAllSlides() { return slidesRepository.findAll(); }

    public Slides getSlideById(Integer slideId) {
        return slidesRepository.findById(slideId).orElseThrow(() -> new EntityNotFoundException("Slide not found " + slideId));
    }

    public List<Slides> getSlidesByChat (Chats chat) {
        return slidesRepository.findByChat(chat);
    }

    public Slides addSlide(Short num, Integer chatId) throws IOException {
        Chats chat = chatsRepository.findById(chatId).orElseThrow(() -> new EntityNotFoundException("Chat not found " + chatId));

        Slides slide = new Slides();
        slide.setChat(chat);
        slide.setNum(num);

        return slidesRepository.save(slide);
    }

    public Slides updateSlide(Integer slideId, Slides updatedSlide) {
        Slides existing = getSlideById(slideId);
        existing.setNum(updatedSlide.getNum());
        return slidesRepository.save(existing);
    }

    public void deleteSlide(Integer slideId) {
        if(!slidesRepository.existsById(slideId)) {
            throw new EntityNotFoundException("Slide not found " + slideId);
        }
        slidesRepository.deleteById(slideId);
    }
}
