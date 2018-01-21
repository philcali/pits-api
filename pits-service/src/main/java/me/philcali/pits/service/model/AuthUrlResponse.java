package me.philcali.pits.service.model;

public class AuthUrlResponse {
    private final String authUrl;

    public AuthUrlResponse(final String authUrl) {
        this.authUrl = authUrl;
    }

    public String getAuthUrl() {
        return authUrl;
    }
}
