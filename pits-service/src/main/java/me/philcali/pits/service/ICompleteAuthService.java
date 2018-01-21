package me.philcali.pits.service;

import java.util.function.Function;

import me.philcali.pits.service.model.CompleteAuthRequest;
import me.philcali.pits.service.model.CompleteAuthResponse;

public interface ICompleteAuthService extends Function<CompleteAuthRequest, CompleteAuthResponse> {
    @Override
    CompleteAuthResponse apply(CompleteAuthRequest request);
}
