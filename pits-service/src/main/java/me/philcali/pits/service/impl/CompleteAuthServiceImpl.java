package me.philcali.pits.service.impl;

import java.util.Optional;

import javax.inject.Inject;
import javax.inject.Singleton;

import me.philcali.oauth.api.IClientConfigRepository;
import me.philcali.oauth.api.IExpiringAuthManager;
import me.philcali.oauth.api.INonceRepository;
import me.philcali.oauth.api.ITokenRespository;
import me.philcali.oauth.api.model.IClientConfig;
import me.philcali.oauth.api.model.IExpiringToken;
import me.philcali.oauth.api.model.IProfile;
import me.philcali.pits.data.IUserRepository;
import me.philcali.pits.data.model.IUser;
import me.philcali.pits.data.model.transfer.User;
import me.philcali.pits.service.ICompleteAuthService;
import me.philcali.pits.service.model.CompleteAuthRequest;
import me.philcali.pits.service.model.CompleteAuthResponse;
import me.philcali.pits.service.response.UnauthorizedException;

@Singleton
public class CompleteAuthServiceImpl implements ICompleteAuthService {
    private static final String API_CREDS = "PITS";
    private static final String CONSOLE_USER = "console:read";

    private final IExpiringAuthManager login;
    private final ITokenRespository tokens;
    private final IUserRepository users;
    private final INonceRepository nonces;
    private final IClientConfigRepository credentials;

    @Inject
    public CompleteAuthServiceImpl(
            final IExpiringAuthManager login,
            final IUserRepository users,
            final INonceRepository nonces,
            final ITokenRespository tokens,
            final IClientConfigRepository credentials) {
        this.login = login;
        this.users = users;
        this.nonces = nonces;
        this.tokens = tokens;
        this.credentials = credentials;
    }

    @Override
    public CompleteAuthResponse apply(final CompleteAuthRequest request) {
        Optional.ofNullable(request.getError())
                .map(UnauthorizedException::new)
                .ifPresent(error -> { throw error; });
        return nonces.verify(request.getNonce(), request.getType()).map(nonce -> {
            final IExpiringToken token = login.exchange(request.getCode());
            final IProfile profile = login.me(token);
            final IUser user = users.get(profile.getEmail()).orElseGet(() -> User.builder()
                    .withEmailAddress(profile.getEmail())
                    .withFirstName(profile.getFirstName())
                    .withLastName(profile.getLastName())
                    .withImage(profile.getImage())
                    .build());
            users.save(user);
            final IClientConfig clientCreds = credentials.listByOwners(user.getEmailAddress())
                    .getItems().stream()
                    .filter(creds -> creds.getApi().equals(API_CREDS))
                    .findFirst()
                    .orElseGet(() -> credentials.generate(profile.getEmail(), API_CREDS, CONSOLE_USER));
            return new CompleteAuthResponse(tokens.generate(clientCreds));
        })
        .orElseThrow(UnauthorizedException::new);
    }
}
