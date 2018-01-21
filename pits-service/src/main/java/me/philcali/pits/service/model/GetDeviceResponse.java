package me.philcali.pits.service.model;

import me.philcali.pits.data.model.IDevice;

public class GetDeviceResponse {
    private final IDevice device;

    public GetDeviceResponse(final IDevice device) {
        this.device = device;
    }

    public IDevice getDevice() {
        return device;
    }
}
