package me.philcali.pits.service;

import javax.inject.Inject;

import me.philcali.pits.data.IDeviceOwnerRepository;
import me.philcali.pits.data.IDeviceRepository;
import me.philcali.pits.service.model.ListDevicesRequest;
import me.philcali.pits.service.model.ListDevicesResponse;
import me.philcali.pits.service.session.ISessionRepository;
import me.philcali.service.annotations.GET;
import me.philcali.service.binding.IOperation;
import me.philcali.service.binding.response.UnauthorizedException;

public class ListDevicesService implements IOperation<ListDevicesRequest, ListDevicesResponse> {
    private final IDeviceRepository devices;
    private final IDeviceOwnerRepository owners;
    private final ISessionRepository sessions;

    @Inject
    public ListDevicesService(
            final IDeviceRepository devices,
            final IDeviceOwnerRepository owners,
            final ISessionRepository sessions) {
        this.devices = devices;
        this.owners = owners;
        this.sessions = sessions;
    }

    @Override
    @GET("/devices")
    public ListDevicesResponse apply(final ListDevicesRequest input) {
        return sessions.get()
                .map(owner -> owners.listDevicesByOwner(owner.getUserId()))
                .map(results -> {
                    return new ListDevicesResponse(null, devices.batchGetByOwners(results.getItems()));
                })
                .orElseThrow(UnauthorizedException::new);
    }
}
