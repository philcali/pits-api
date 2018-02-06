package me.philcali.pits.service.model;

import me.philcali.service.annotations.request.QueryParam;

public class ListDevicesRequest {
    @QueryParam
    private String nextToken;

    public String getNextToken() {
        return nextToken;
    }

    public void setNextToken(String nextToken) {
        this.nextToken = nextToken;
    }
}
