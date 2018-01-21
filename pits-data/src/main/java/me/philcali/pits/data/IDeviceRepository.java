package me.philcali.pits.data;

import java.util.List;
import java.util.Optional;

import me.philcali.pits.data.model.IDevice;
import me.philcali.pits.data.model.IDeviceOwner;

public interface IDeviceRepository {
    List<IDevice> batchGetByOwners(List<IDeviceOwner> owners);

    Optional<IDevice> get(String deviceId);

    void save(IDevice device);
}
