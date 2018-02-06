package me.philcali.pits.service;

import java.util.function.Function;

import me.philcali.pits.service.model.GetDeviceRegistrationUrlRequest;
import me.philcali.pits.service.model.GetDeviceRegistrationUrlResponse;
import me.philcali.service.annotations.GET;
import me.philcali.service.annotations.Resource;

@Resource("/devices/{id}/registration")
public interface IGetDeviceRegistrationUrlService
        extends Function<GetDeviceRegistrationUrlRequest, GetDeviceRegistrationUrlResponse> {
    @Override
    @GET
    GetDeviceRegistrationUrlResponse apply(GetDeviceRegistrationUrlRequest request);
}
