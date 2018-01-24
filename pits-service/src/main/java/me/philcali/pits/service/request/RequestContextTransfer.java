package me.philcali.pits.service.request;

import java.util.Map;

public class RequestContextTransfer implements IRequestContext {
    private String accountId;
    private String apiId;
    private Map<String, String> authorizer;
    private String protocol;
    private String requestId;
    private String stage;
    private String resourceId;

    @Override
    public String getAccountId() {
        return accountId;
    }

    @Override
    public String getApiId() {
        return apiId;
    }

    @Override
    public Map<String, String> getAuthorizer() {
        return authorizer;
    }

    @Override
    public String getProtocol() {
        return protocol;
    }

    @Override
    public String getRequestId() {
        return requestId;
    }

    @Override
    public String getResourceId() {
        return resourceId;
    }

    @Override
    public String getStage() {
        return stage;
    }

    public void setAccountId(String accountId) {
        this.accountId = accountId;
    }

    public void setApiId(String apiId) {
        this.apiId = apiId;
    }

    public void setAuthorizer(Map<String, String> authorizer) {
        this.authorizer = authorizer;
    }

    public void setProtocol(String protocol) {
        this.protocol = protocol;
    }

    public void setRequestId(String requestId) {
        this.requestId = requestId;
    }

    public void setResourceId(String resourceId) {
        this.resourceId = resourceId;
    }

    public void setStage(String stage) {
        this.stage = stage;
    }
}
