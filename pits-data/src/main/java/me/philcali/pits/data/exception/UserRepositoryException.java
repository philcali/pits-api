package me.philcali.pits.data.exception;

public class UserRepositoryException extends RuntimeException {
    /**
     *
     */
    private static final long serialVersionUID = 445289373753251978L;

    public UserRepositoryException(final Throwable t) {
        super(t);
    }
}
