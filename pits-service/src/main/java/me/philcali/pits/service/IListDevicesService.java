package me.philcali.pits.service;

import java.util.function.Function;

import me.philcali.pits.service.model.ListDevicesRequest;
import me.philcali.pits.service.model.ListDevicesResponse;
import me.philcali.service.annotations.GET;
import me.philcali.service.annotations.Resource;

@Resource("/devices")
public interface IListDevicesService extends Function<ListDevicesRequest, ListDevicesResponse> {
    @Override
    @GET
    ListDevicesResponse apply(ListDevicesRequest request);
}
