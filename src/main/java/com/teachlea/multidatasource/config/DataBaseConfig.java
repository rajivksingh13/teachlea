package com.teachlea.multidatasource.config;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;
import javax.sql.DataSource;
import java.util.HashMap;
import java.util.Map;

@ConfigurationProperties(prefix = "db")
@Component
@Data
public class DataBaseConfig {
    private String url;
    private String username;
    private String driver;
    private String password;
    private String maximumPoolSize;
    private String minimumIdle;
    private String idleTimeout;
    private String maxLifetime;
    private String connectionTimeout;
    private Map<String, DataBaseConfig> configurations = new HashMap<>();

    DataSource createDataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(url);
        config.setUsername(username);
        config.setPassword(password);
        config.setDriverClassName(driver);
        config.setMaximumPoolSize(Integer.parseInt(maximumPoolSize));
        config.setMinimumIdle(Integer.parseInt(minimumIdle));
        config.setIdleTimeout(Long.parseLong(idleTimeout));
        config.setMaxLifetime(Long.parseLong(maxLifetime));
        config.setConnectionTimeout(Long.parseLong(connectionTimeout));
        HikariDataSource dataSource = new HikariDataSource(config);
        return dataSource;
    }

    Map<Object, Object> createTargetDataSources() {
        Map<Object, Object> result = new HashMap<>();
        configurations.forEach((key, value) ->  result.put(key, value.createDataSource()));
        return result;
    }

}
