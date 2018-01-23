package me.philcali.pits.service.model;

import me.philcali.oauth.api.model.IExpiringToken;

public class CompleteAuthResponse {
    private final IExpiringToken session;

    public CompleteAuthResponse(final IExpiringToken session) {
        this.session = session;
    }

    public IExpiringToken getSession() {
        return session;
    }
}
