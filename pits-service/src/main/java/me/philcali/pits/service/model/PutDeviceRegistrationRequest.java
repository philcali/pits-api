package me.philcali.pits.service.model;

import me.philcali.pits.data.model.transfer.Device;
import me.philcali.service.annotations.request.Body;
import me.philcali.service.annotations.request.PathParam;
import me.philcali.service.annotations.request.QueryParam;

public class PutDeviceRegistrationRequest {
    @QueryParam
    private String code;
    @PathParam
    private String id;
    @Body
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
