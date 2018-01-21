package me.philcali.pits.service;

import java.util.function.Function;

import me.philcali.pits.service.model.GetDeviceRegistrationUrlRequest;
import me.philcali.pits.service.model.GetDeviceRegistrationUrlResponse;

public interface IGetDeviceRegistrationUrlService
        extends Function<GetDeviceRegistrationUrlRequest, GetDeviceRegistrationUrlResponse> {
    @Override
    GetDeviceRegistrationUrlResponse apply(GetDeviceRegistrationUrlRequest request);
}
