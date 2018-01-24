package me.philcali.pits.service.response;

public class UnauthorizedException extends RuntimeException {
    private static final long serialVersionUID = 6058731632936560167L;

    public UnauthorizedException() {
        super();
    }

    public UnauthorizedException(final String message) {
        super(message);
    }
}
