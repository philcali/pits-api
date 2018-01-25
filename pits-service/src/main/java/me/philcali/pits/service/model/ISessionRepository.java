package me.philcali.pits.service.model;

import java.util.Optional;

import me.philcali.oauth.api.model.IUserClientConfig;

public interface ISessionRepository {
    String API_CREDS = "PITS";

    Optional<IUserClientConfig> get();
}
