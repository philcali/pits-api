package me.philcali.pits.service;

import javax.inject.Inject;

import me.philcali.oauth.api.IAuthManager;
import me.philcali.oauth.api.INonceRepository;
import me.philcali.oauth.spi.OAuthProviders;
import me.philcali.pits.service.model.AuthUrlRequest;
import me.philcali.pits.service.model.AuthUrlResponse;
import me.philcali.service.annotations.GET;
import me.philcali.service.binding.IOperation;

public class GetAuthUrlService implements IOperation<AuthUrlRequest, AuthUrlResponse> {
    private final INonceRepository nonces;

    @Inject
    public GetAuthUrlService(final INonceRepository nonces) {
        this.nonces = nonces;
    }

    @Override
    @GET("/auth")
    public AuthUrlResponse apply(final AuthUrlRequest input) {
        IAuthManager manager = OAuthProviders.getAuthManager(input.getType(), IAuthManager.class);
        return new AuthUrlResponse(manager.getAuthUrl(nonces.generate(input.getType()).getId()));
    }

}
