package me.philcali.pits.data.exception;

public class DeviceOwnerRepositoryException extends RuntimeException {
    private static final long serialVersionUID = -3486799165937962595L;

    public DeviceOwnerRepositoryException(final Throwable t) {
        super(t);
    }
}
