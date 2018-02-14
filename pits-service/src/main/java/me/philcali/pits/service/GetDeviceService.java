package me.philcali.pits.service;

import javax.inject.Inject;

import me.philcali.pits.data.IDeviceOwnerRepository;
import me.philcali.pits.data.IDeviceRepository;
import me.philcali.pits.service.model.GetDeviceRequest;
import me.philcali.pits.service.model.GetDeviceResponse;
import me.philcali.pits.service.session.ISessionRepository;
import me.philcali.service.annotations.GET;
import me.philcali.service.binding.IOperation;
import me.philcali.service.binding.response.NotFoundException;

public class GetDeviceService implements IOperation<GetDeviceRequest, GetDeviceResponse> {
    private final IDeviceRepository devices;
    private final IDeviceOwnerRepository owners;
    private final ISessionRepository sessions;

    @Inject
    public GetDeviceService(
            final IDeviceRepository devices,
            final IDeviceOwnerRepository owners,
            final ISessionRepository sessions) {
        this.devices = devices;
        this.owners = owners;
        this.sessions = sessions;
    }

    @Override
    @GET("/device/{id}")
    public GetDeviceResponse apply(final GetDeviceRequest input) {
        return sessions.get()
                .flatMap(owner -> owners.get(input.getId(), owner.getUserId()))
                .flatMap(deviceOwner -> devices.get(deviceOwner.getDeviceId()))
                .map(GetDeviceResponse::new)
                .orElseThrow(NotFoundException::new);
    }
}
