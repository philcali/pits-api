package me.philcali.pits.service.response;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class Response implements IResponse {
    public static class Builder {
        private int statusCode;
        private Map<String, String> headers;
        private String body;
        private Throwable exception;

        public Response build() {
            return new Response(this);
        }

        public String getBody() {
            return body;
        }

        public Throwable getException() {
            return exception;
        }

        public Map<String, String> getHeaders() {
            return headers;
        }

        public int getStatusCode() {
            return statusCode;
        }

        public Builder withBody(final String body) {
            this.body = body;
            return this;
        }

        public Builder withException(final Throwable exception) {
            this.exception = exception;
            return this;
        }

        public Builder withHeaders(final Map<String, String> headers) {
            this.headers = headers;
            return this;
        }

        public Builder withHeaders(final String name, final String value) {
            final Map<String, String> newHeaders = Optional.ofNullable(headers).orElseGet(HashMap::new);
            newHeaders.put(name, value);
            withHeaders(newHeaders);
            return this;
        }

        public Builder withStatusCode(final int statusCode) {
            this.statusCode = statusCode;
            return this;
        }
    }

    public static Builder builder() {
        return new Builder().withStatusCode(200);
    }

    public static Response forbidden() {
        return builder().withStatusCode(403).build();
    }

    public static Builder from(IResponse response) {
        return builder()
                .withBody(response.getBody())
                .withException(response.getException())
                .withStatusCode(response.getStatusCode())
                .withHeaders(response.getHeaders());
    }

    public static Response internalError(Throwable ex) {
        return builder().withException(ex).withStatusCode(500).build();
    }

    public static Response noContent() {
        return builder().withStatusCode(204).build();
    }

    public static Response ok() {
        return builder().build();
    }

    public static Response ok(final String content) {
        return builder().withBody(content).build();
    }

    public static Response unauthorized() {
        return builder().withStatusCode(401).build();
    }

    private final int statusCode;
    private final Map<String, String> headers;
    private final String body;
    private final Throwable exception;

    private Response(final Builder builder) {
        this.statusCode = builder.getStatusCode();
        this.headers = builder.getHeaders();
        this.body = builder.getBody();
        this.exception = builder.getException();
    }

    @Override
    public String getBody() {
        return body;
    }

    @Override
    public Throwable getException() {
        return exception;
    }

    @Override
    public Map<String, String> getHeaders() {
        return headers;
    }

    @Override
    public int getStatusCode() {
        return statusCode;
    }

}
