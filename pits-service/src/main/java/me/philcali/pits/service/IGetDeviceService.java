package me.philcali.pits.service;

import java.util.function.Function;

import me.philcali.pits.service.model.GetDeviceRequest;
import me.philcali.pits.service.model.GetDeviceResponse;
import me.philcali.service.annotations.GET;
import me.philcali.service.annotations.Resource;

@Resource("/devices/{id}")
public interface IGetDeviceService extends Function<GetDeviceRequest, GetDeviceResponse> {
    @Override
    @GET
    GetDeviceResponse apply(GetDeviceRequest request);
}
