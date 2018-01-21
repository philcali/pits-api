package me.philcali.pits.service;

import java.util.function.Function;

import me.philcali.pits.service.model.ListDevicesRequest;
import me.philcali.pits.service.model.ListDevicesResponse;

public interface IListDevicesService extends Function<ListDevicesRequest, ListDevicesResponse> {
    @Override
    ListDevicesResponse apply(ListDevicesRequest request);
}
