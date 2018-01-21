package me.philcali.pits.service.model;

public class GetDeviceRegistrationUrlResponse {
    private final String registrationUrl;

    public GetDeviceRegistrationUrlResponse(final String registrationUrl) {
        this.registrationUrl = registrationUrl;
    }

    public String getRegistrationUrl() {
        return registrationUrl;
    }
}
