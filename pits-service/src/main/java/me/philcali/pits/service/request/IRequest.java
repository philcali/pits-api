package me.philcali.pits.service.request;

import java.util.Map;

public interface IRequest {
    String getBody();
    Map<String, String> getHeaders();
    String getHttpMethod();
    String getPath();
    Map<String, String> getPathParameters();
    Map<String, String> getQueryStringParameters();
    IRequestContext getRequestContext();
    String getResource();
    Map<String, String> getStageVariables();
}
