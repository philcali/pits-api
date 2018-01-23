package me.philcali.pits.service.impl;

import javax.inject.Inject;
import javax.inject.Singleton;

import me.philcali.oauth.api.IAuthManager;
import me.philcali.oauth.api.ITokenRespository;
import me.philcali.pits.data.IUserRepository;
import me.philcali.pits.service.ICompleteAuthService;
import me.philcali.pits.service.model.CompleteAuthRequest;
import me.philcali.pits.service.model.CompleteAuthResponse;

@Singleton
public class CompleteAuthServiceImpl implements ICompleteAuthService {
    private final IAuthManager login;
    private final ITokenRespository tokens;
    private final IUserRepository users;

    @Inject
    public CompleteAuthServiceImpl(
            final IAuthManager login,
            final IUserRepository users,
            final ITokenRespository tokens) {
        this.login = login;
        this.users = users;
        this.tokens = tokens;
    }

    @Override
    public CompleteAuthResponse apply(final CompleteAuthRequest request) {
        // TODO: fill this out
        return null;
    }
}
