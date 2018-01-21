package me.philcali.pits.service;

import java.util.function.Supplier;

import me.philcali.pits.service.model.GetUserResponse;

public interface IGetMeService extends Supplier<GetUserResponse> {
    @Override
    GetUserResponse get();
}
