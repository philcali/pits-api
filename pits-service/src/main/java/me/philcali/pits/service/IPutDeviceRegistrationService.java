package me.philcali.pits.service;

import java.util.function.Function;

import me.philcali.pits.service.model.PutDeviceRegistrationRequest;
import me.philcali.pits.service.model.PutDeviceRegistrationResponse;
import me.philcali.service.annotations.PUT;
import me.philcali.service.annotations.Resource;

@Resource("/devices/{id}/registration")
public interface IPutDeviceRegistrationService
        extends Function<PutDeviceRegistrationRequest, PutDeviceRegistrationResponse> {
    @Override
    @PUT
    PutDeviceRegistrationResponse apply(PutDeviceRegistrationRequest request);
}
