package com.teachlea.exception;

import lombok.extern.slf4j.Slf4j;
import org.wildfly.security.auth.AuthenticationException;

import javax.ws.rs.core.Response;
import javax.ws.rs.ext.ExceptionMapper;
import javax.ws.rs.ext.Provider;

@Slf4j
@Provider
public class AuthenticationExceptionMapper implements ExceptionMapper<AuthenticationException> {
    @Override
    public Response toResponse(AuthenticationException e) {
        return Response.status(Response.Status.UNAUTHORIZED).entity("Authentication information is missing or invalid").build();
    }
}