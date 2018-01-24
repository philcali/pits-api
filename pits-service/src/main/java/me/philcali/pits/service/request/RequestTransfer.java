package me.philcali.pits.service.request;

import java.util.Map;

public class RequestTransfer implements IRequest {
    private String body;
    private String httpMethod;
    private String path;
    private String resource;
    private RequestContextTransfer requestContext;
    private Map<String, String> pathParameters;
    private Map<String, String> queryStringParameters;
    private Map<String, String> headers;
    private Map<String, String> stageVariables;

    @Override
    public String getBody() {
        return body;
    }

    @Override
    public Map<String, String> getHeaders() {
        return headers;
    }

    @Override
    public String getHttpMethod() {
        return httpMethod;
    }

    @Override
    public String getPath() {
        return path;
    }

    @Override
    public Map<String, String> getPathParameters() {
        return pathParameters;
    }

    @Override
    public Map<String, String> getQueryStringParameters() {
        return queryStringParameters;
    }

    @Override
    public IRequestContext getRequestContext() {
        return requestContext;
    }

    @Override
    public String getResource() {
        return resource;
    }

    @Override
    public Map<String, String> getStageVariables() {
        return stageVariables;
    }

    public void setBody(String body) {
        this.body = body;
    }

    public void setHeaders(Map<String, String> headers) {
        this.headers = headers;
    }

    public void setHttpMethod(String httpMethod) {
        this.httpMethod = httpMethod;
    }

    public void setPath(String path) {
        this.path = path;
    }

    public void setPathParameters(Map<String, String> pathParameters) {
        this.pathParameters = pathParameters;
    }

    public void setQueryStringParameters(Map<String, String> queryStringParameters) {
        this.queryStringParameters = queryStringParameters;
    }

    public void setRequestContext(RequestContextTransfer requestContext) {
        this.requestContext = requestContext;
    }

    public void setResource(String resource) {
        this.resource = resource;
    }

    public void setStageVariables(Map<String, String> stageVariables) {
        this.stageVariables = stageVariables;
    }

}
