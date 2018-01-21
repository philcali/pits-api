package me.philcali.pits.service;

import java.util.function.Function;

import me.philcali.pits.service.model.AuthUrlRequest;
import me.philcali.pits.service.model.AuthUrlResponse;

public interface IGetAuthUrlService extends Function<AuthUrlRequest, AuthUrlResponse> {
    @Override
    AuthUrlResponse apply(AuthUrlRequest input);
}
