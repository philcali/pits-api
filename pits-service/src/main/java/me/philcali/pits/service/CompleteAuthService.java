package me.philcali.pits.service;

import java.util.Optional;

import javax.inject.Inject;

import me.philcali.oauth.api.IClientConfigRepository;
import me.philcali.oauth.api.IExpiringAuthManager;
import me.philcali.oauth.api.INonceRepository;
import me.philcali.oauth.api.ITokenRepository;
import me.philcali.oauth.api.model.IExpiringToken;
import me.philcali.oauth.api.model.IProfile;
import me.philcali.oauth.api.model.IUserClientConfig;
import me.philcali.oauth.spi.OAuthProviders;
import me.philcali.pits.data.IUserRepository;
import me.philcali.pits.data.model.IUser;
import me.philcali.pits.data.model.transfer.User;
import me.philcali.pits.service.model.CompleteAuthRequest;
import me.philcali.pits.service.model.CompleteAuthResponse;
import me.philcali.pits.service.session.ISessionRepository;
import me.philcali.service.annotations.GET;
import me.philcali.service.binding.IOperation;
import me.philcali.service.binding.response.UnauthorizedException;

public class CompleteAuthService implements IOperation<CompleteAuthRequest, CompleteAuthResponse> {
    private static final String CONSOLE_USER = "console:read";

    private final ITokenRepository tokens;
    private final IUserRepository users;
    private final INonceRepository nonces;
    private final IClientConfigRepository credentials;

    @Inject
    public CompleteAuthService(
            final IUserRepository users,
            final INonceRepository nonces,
            final ITokenRepository tokens,
            final IClientConfigRepository credentials) {
        this.users = users;
        this.nonces = nonces;
        this.tokens = tokens;
        this.credentials = credentials;
    }

    @Override
    @GET("/auth/{type}")
    public CompleteAuthResponse apply(final CompleteAuthRequest request) {
        Optional.ofNullable(request.getError())
                .map(UnauthorizedException::new)
                .ifPresent(error -> { throw error; });
        return nonces.verify(request.getNonce(), request.getType()).map(nonce -> {
            final IExpiringAuthManager login = OAuthProviders.getAuthManager(request.getType(), IExpiringAuthManager.class);
            final IExpiringToken token = login.exchange(request.getCode());
            final IProfile profile = login.me(token);
            final IUser user = users.get(profile.getEmail()).orElseGet(() -> User.builder()
                    .withEmailAddress(profile.getEmail())
                    .withFirstName(profile.getFirstName())
                    .withLastName(profile.getLastName())
                    .withImage(profile.getImage())
                    .build());
            users.save(user);
            final IUserClientConfig clientCreds = credentials.listByOwners(user.getEmailAddress())
                    .getItems().stream()
                    .filter(creds -> creds.getApi().equals(ISessionRepository.API_CREDS))
                    .findFirst()
                    .orElseGet(() -> credentials.generate(profile.getEmail(), ISessionRepository.API_CREDS, CONSOLE_USER));
            return new CompleteAuthResponse(tokens.generate(clientCreds));
        })
        .orElseThrow(UnauthorizedException::new);
    }
}
