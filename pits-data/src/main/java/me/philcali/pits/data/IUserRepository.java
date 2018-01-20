package me.philcali.pits.data;

import java.util.Optional;

import me.philcali.pits.data.model.IUser;

public interface IUserRepository {
    Optional<IUser> get(String emailAddress);

    void save(IUser user);
}
