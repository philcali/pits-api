package me.philcali.pits.data;

import java.util.Optional;

import me.philcali.pits.data.model.IDevice;

public interface IDeviceRepository {
    Optional<IDevice> get(String deviceId);

    void save(IDevice device);
}
