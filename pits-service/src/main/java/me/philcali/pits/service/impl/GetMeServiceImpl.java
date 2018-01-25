package me.philcali.pits.service.impl;

import javax.inject.Inject;

import me.philcali.pits.data.IUserRepository;
import me.philcali.pits.service.IGetMeService;
import me.philcali.pits.service.model.GetUserResponse;
import me.philcali.pits.service.model.ISessionRepository;
import me.philcali.pits.service.response.UnauthorizedException;

public class GetMeServiceImpl implements IGetMeService {
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
    public GetUserResponse get() {
        return sessions.get()
                .flatMap(creds -> users.get(creds.getUserId()))
                .map(GetUserResponse::new)
                .orElseThrow(UnauthorizedException::new);
    }

}
