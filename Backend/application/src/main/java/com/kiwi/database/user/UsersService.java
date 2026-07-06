package com.kiwi.database.user;

import jakarta.persistence.EntityNotFoundException;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class UsersService {
    private final UsersRepository usersRepository;

    public UsersService(UsersRepository usersRepository) {
        this.usersRepository = usersRepository;
    }

    public List<Users> getAllUsers() {
        return usersRepository.findAll();
    }

    public Users getUserById (Integer userId) {
        return usersRepository.findById(userId).orElseThrow(() -> new EntityNotFoundException("User not found " + userId));
    }

    public Users createUser(Users user) {
        return usersRepository.save(user);
    }

    public Users updateUser(Integer userId, Users updatedUser) {
        Users existing = getUserById(userId);
        existing.setDepartment(updatedUser.getDepartment());
        return usersRepository.save(existing);
    }

    public void deleteUser(Integer userId) {
        if(!usersRepository.existsById(userId)) {
            throw new EntityNotFoundException("User not found " + userId);
        }
        usersRepository.deleteById(userId);
    }
}
