package me.philcali.pits.service;

import java.util.function.Function;

import me.philcali.pits.service.model.GetDeviceRequest;
import me.philcali.pits.service.model.GetDeviceResponse;

public interface IGetDeviceService extends Function<GetDeviceRequest, GetDeviceResponse> {
    @Override
    GetDeviceResponse apply(GetDeviceRequest request);
}
