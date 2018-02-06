package me.philcali.pits.service.session;

import java.util.Optional;

import me.philcali.oauth.api.model.IUserClientConfig;

public interface ISessionRepository {
    String API_CREDS = "PITS";

    Optional<IUserClientConfig> get();
}
