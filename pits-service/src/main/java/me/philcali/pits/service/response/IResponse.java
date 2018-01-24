package me.philcali.pits.service.response;

import java.util.Map;

public interface IResponse {
    String getBody();
    Throwable getException();
    Map<String, String> getHeaders();
    int getStatusCode();
}
