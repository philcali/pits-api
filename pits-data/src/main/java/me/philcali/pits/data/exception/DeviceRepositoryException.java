package me.philcali.pits.data.exception;

public class DeviceRepositoryException extends RuntimeException {
    private static final long serialVersionUID = -8605461982695418866L;

    public DeviceRepositoryException(final Throwable t) {
        super(t);
    }
}
