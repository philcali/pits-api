package me.philcali.pits.service.model;

import me.philcali.pits.data.model.transfer.Device;

public class PutDeviceRegistrationRequest {
    private String code;
    private String id;
    private Device device;

    public String getCode() {
        return code;
    }

    public Device getDevice() {
        return device;
    }

    public String getId() {
        return id;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public void setDevice(Device device) {
        this.device = device;
    }

    public void setId(String id) {
        this.id = id;
    }
}
