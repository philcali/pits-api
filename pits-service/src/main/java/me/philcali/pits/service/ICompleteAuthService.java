package me.philcali.pits.service;

import java.util.function.Function;

import me.philcali.pits.service.model.CompleteAuthRequest;
import me.philcali.pits.service.model.CompleteAuthResponse;
import me.philcali.service.annotations.GET;
import me.philcali.service.annotations.Resource;

@Resource("/auth/{type}")
public interface ICompleteAuthService extends Function<CompleteAuthRequest, CompleteAuthResponse> {
    @Override
    @GET
    CompleteAuthResponse apply(CompleteAuthRequest request);
}
