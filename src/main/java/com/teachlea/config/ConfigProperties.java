package com.teachlea.config;

import io.smallrye.config.ConfigMapping;

@ConfigMapping(prefix = "teachlea", namingStrategy = ConfigMapping.NamingStrategy.VERBATIM)
public interface ConfigProperties {

    Authentication Authentication();

    interface Authentication{
        String userName();
        String password();
    }
}
