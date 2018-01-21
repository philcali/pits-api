package me.philcali.pits.service.model;

import me.philcali.pits.data.model.IUser;

public class GetUserResponse {
    private final IUser user;

    public GetUserResponse(final IUser user) {
        this.user = user;
    }

    public IUser getUser() {
        return user;
    }
}
