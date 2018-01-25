package me.philcali.pits.service.request;

import java.util.Optional;

import javax.inject.Inject;

import me.philcali.oauth.api.IClientConfigRepository;
import me.philcali.oauth.api.ITokenRepository;
import me.philcali.oauth.api.model.IUserClientConfig;
import me.philcali.pits.service.model.ISessionRepository;

public class SessionRespositoryRequest implements ISessionRepository {
    private final IClientConfigRepository credentials;
    private final ITokenRepository tokens;
    private final IRequest request;

    @Inject
    public SessionRespositoryRequest(
            final IClientConfigRepository credentials,
            final ITokenRepository tokens,
            final IRequest request) {
        this.credentials = credentials;
        this.tokens = tokens;
        this.request = request;
    }

    @Override
    public Optional<IUserClientConfig> get() {
        return Optional.ofNullable(request.getHeaders().get("Authorization"))
                .map(authorization -> authorization.replaceAll("Bearer\\s*", ""))
                .flatMap(tokenId -> tokens.get(tokenId, API_CREDS))
                .flatMap(token -> credentials.get(API_CREDS, token.getClientId()));
    }

}
