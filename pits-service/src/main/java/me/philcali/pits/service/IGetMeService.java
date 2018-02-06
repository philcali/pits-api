package me.philcali.pits.service;

import java.util.function.Supplier;

import me.philcali.pits.service.model.GetUserResponse;
import me.philcali.service.annotations.GET;
import me.philcali.service.annotations.Resource;

@Resource("/me")
public interface IGetMeService extends Supplier<GetUserResponse> {
    @Override
    @GET
    GetUserResponse get();
}
