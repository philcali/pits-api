package me.philcali.pits.service;

import javax.inject.Inject;

import me.philcali.pits.data.IUserRepository;
import me.philcali.pits.service.model.GetUserResponse;
import me.philcali.pits.service.session.ISessionRepository;
import me.philcali.service.annotations.GET;
import me.philcali.service.binding.IEmptyInputOperation;
import me.philcali.service.binding.response.UnauthorizedException;

public class GetMeServiceImpl implements IEmptyInputOperation<GetUserResponse> {
    private final IUserRepository users;
    private final ISessionRepository sessions;

    @Inject
    public GetMeServiceImpl(
            final IUserRepository users,
            final ISessionRepository sessions) {
        this.users = users;
        this.sessions = sessions;
    }

    @Override
    @GET("/me")
    public GetUserResponse get() {
        return sessions.get()
                .flatMap(creds -> users.get(creds.getUserId()))
                .map(GetUserResponse::new)
                .orElseThrow(UnauthorizedException::new);
    }

}
