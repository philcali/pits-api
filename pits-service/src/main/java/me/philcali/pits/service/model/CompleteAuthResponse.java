package me.philcali.pits.service.model;

public class CompleteAuthResponse {
    private final String redirectUrl;

    public CompleteAuthResponse(final String redirectUrl) {
        this.redirectUrl = redirectUrl;
    }

    public String getRedirectUrl() {
        return redirectUrl;
    }
}
