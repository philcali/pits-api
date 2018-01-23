package me.philcali.pits.service.model;

import me.philcali.oauth.api.model.IToken;

public class PutDeviceRegistrationResponse {
    private final IToken session;

    public PutDeviceRegistrationResponse(final IToken session) {
        this.session = session;
    }

    public IToken getSession() {
        return session;
    }
}
