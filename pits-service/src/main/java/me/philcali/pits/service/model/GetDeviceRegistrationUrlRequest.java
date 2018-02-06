package me.philcali.pits.service.model;

import me.philcali.service.annotations.request.PathParam;

public class GetDeviceRegistrationUrlRequest {
    @PathParam
    private String id;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }
}
