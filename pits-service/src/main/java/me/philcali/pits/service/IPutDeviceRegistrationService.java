package me.philcali.pits.service;

import java.util.function.Function;

import me.philcali.pits.service.model.PutDeviceRegistrationRequest;
import me.philcali.pits.service.model.PutDeviceRegistrationResponse;

public interface IPutDeviceRegistrationService
        extends Function<PutDeviceRegistrationRequest, PutDeviceRegistrationResponse> {
    @Override
    PutDeviceRegistrationResponse apply(PutDeviceRegistrationRequest request);
}
