package me.philcali.pits.service;

import java.util.function.Function;

import me.philcali.pits.service.model.AuthUrlRequest;
import me.philcali.pits.service.model.AuthUrlResponse;
import me.philcali.service.annotations.GET;
import me.philcali.service.annotations.Resource;

@Resource("/auth")
public interface IGetAuthUrlService extends Function<AuthUrlRequest, AuthUrlResponse> {
    @Override
    @GET
    AuthUrlResponse apply(AuthUrlRequest input);
}
