package me.philcali.pits.data;

import java.util.List;
import java.util.Optional;

import me.philcali.pits.data.model.IDeviceOwner;
import me.philcali.pits.data.model.IUser;

public interface IUserRepository {
    List<IUser> batchGetByOwners(List<IDeviceOwner> owners);

    Optional<IUser> get(String emailAddress);

    void save(IUser user);
}
