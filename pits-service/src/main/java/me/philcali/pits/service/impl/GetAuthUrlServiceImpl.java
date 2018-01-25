package me.philcali.pits.service.impl;

import javax.inject.Inject;

import me.philcali.oauth.api.IAuthManager;
import me.philcali.oauth.api.INonceRepository;
import me.philcali.oauth.spi.OAuthProviders;
import me.philcali.pits.service.IGetAuthUrlService;
import me.philcali.pits.service.model.AuthUrlRequest;
import me.philcali.pits.service.model.AuthUrlResponse;

public class GetAuthUrlServiceImpl implements IGetAuthUrlService {
    private final INonceRepository nonces;

    @Inject
    public GetAuthUrlServiceImpl(final INonceRepository nonces) {
        this.nonces = nonces;
    }

    @Override
    public AuthUrlResponse apply(final AuthUrlRequest input) {
        IAuthManager manager = OAuthProviders.getAuthManager(input.getType(), IAuthManager.class);
        return new AuthUrlResponse(manager.getAuthUrl(nonces.generate(input.getType()).getId()));
    }

}
