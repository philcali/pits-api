package me.philcali.pits.service.model;

import java.util.List;

import me.philcali.pits.data.model.IDevice;

public class ListDevicesResponse {
    private final List<IDevice> devices;
    private final String nextToken;

    public ListDevicesResponse(final String nextToken, final List<IDevice> devices) {
        this.nextToken = nextToken;
        this.devices = devices;
    }

    public List<IDevice> getDevices() {
        return devices;
    }

    public String getNextToken() {
        return nextToken;
    }
}
