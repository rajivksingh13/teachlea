package com.teachlea.filter;


import com.teachlea.config.ConfigProperties;
import lombok.extern.slf4j.Slf4j;
import org.wildfly.security.auth.AuthenticationException;

import javax.inject.Inject;
import javax.ws.rs.container.ContainerRequestContext;
import javax.ws.rs.container.ContainerRequestFilter;
import javax.ws.rs.container.PreMatching;
import javax.ws.rs.core.MultivaluedMap;
import javax.ws.rs.ext.Provider;
import java.io.IOException;
import java.util.Base64;
import java.util.List;
import java.util.StringTokenizer;

/**
 * This filter verifies the access permissions for a user using BASIC Authentication
 * based on username and password provided in request Authorization Header
 */
@Provider
@PreMatching
@Slf4j
public class AuthenticationSecurityFilter implements ContainerRequestFilter {
    private static final String AUTHORIZATION_PROPERTY = "Authorization";
    private static final String AUTHENTICATION_SCHEME = "Basic";
    private static final String COLON = ":";
    private static final int tokenCount = 2;

    @Inject
    ConfigProperties configProperties;

    @Override
    public void filter(ContainerRequestContext requestContext) throws IOException {
        final MultivaluedMap<String, String> headers = requestContext.getHeaders();
        final List<String> authorization = headers.get(AUTHORIZATION_PROPERTY);
        validateAuthHeader(authorization);
        checkAuthentication(authorization, configProperties);

    }

    private void validateAuthHeader(final List<String> authorization) throws AuthenticationException {
        if (authorization == null || authorization.isEmpty()) {
            throw new AuthenticationException();
        }
    }

    private void checkAuthentication(final List<String> authorization, ConfigProperties configProperties) throws AuthenticationException {

        final String encodedUserPassword = authorization.get(0).replaceFirst(AUTHENTICATION_SCHEME + " ", "");
        String usernameAndPassword = null;
        usernameAndPassword = new String(Base64.getDecoder().decode(encodedUserPassword));
        final StringTokenizer tokenizer = new StringTokenizer(usernameAndPassword, COLON);
        log.debug("tokenizer count in checkAuthentication is: {}",tokenizer.countTokens());
        if (tokenizer.countTokens() == tokenCount) {
            final String username = tokenizer.nextToken();
            final String password = tokenizer.nextToken();
            if (!isAuthAllowed(username, password, configProperties)) {
                throw new AuthenticationException();
            }
        } else {
            throw new AuthenticationException();
        }

    }

    private boolean isAuthAllowed(final String username, final String password, ConfigProperties configProperties) {
        boolean isAllowed = false;
        String userName = configProperties.Authentication().userName();
        String passWord = new String(Base64.getDecoder().decode(configProperties.Authentication().password().getBytes()));
        //String passWord = configProperties.Authentication().password();
        isAllowed = userName.equalsIgnoreCase(username) && passWord.equalsIgnoreCase(password);
        return isAllowed;
    }
}
