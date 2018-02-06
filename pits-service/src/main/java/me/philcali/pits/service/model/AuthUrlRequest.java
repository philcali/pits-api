package me.philcali.pits.service.model;

import me.philcali.service.annotations.request.QueryParam;

public class AuthUrlRequest {
    @QueryParam
    private String type;

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }
}
