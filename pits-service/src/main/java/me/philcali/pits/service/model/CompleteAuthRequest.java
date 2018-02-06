package me.philcali.pits.service.model;

import me.philcali.service.annotations.request.PathParam;
import me.philcali.service.annotations.request.QueryParam;

public class CompleteAuthRequest {
    @QueryParam
    private String code;
    @QueryParam
    private String error;
    @PathParam
    private String type;
    @QueryParam
    private String nonce;

    public String getCode() {
        return code;
    }

    public String getError() {
        return error;
    }

    public String getNonce() {
        return nonce;
    }

    public String getType() {
        return type;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public void setError(String error) {
        this.error = error;
    }

    public void setNonce(String nonce) {
        this.nonce = nonce;
    }

    public void setType(String type) {
        this.type = type;
    }

}
