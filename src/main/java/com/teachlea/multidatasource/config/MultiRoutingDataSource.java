package com.teachlea.multidatasource.config;


import com.teachlea.multidatasource.exception.DataSourceLookUpException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.env.Environment;
import org.springframework.jdbc.datasource.lookup.AbstractRoutingDataSource;

public class MultiRoutingDataSource extends AbstractRoutingDataSource {
    @Autowired
    Environment env;

    private final String DEFAULT_LOOKUP_KEY = "test.db.defaultLookUpKey";

    @Override
    protected Object determineCurrentLookupKey() {
        String defaultLookUpkey = env.getProperty(DEFAULT_LOOKUP_KEY);
        if (DBContextHolder.getDataBaseSite() == null) {
            logger.info("Inside If loop MultiRoutingDataSource defaultLookUpkey :" + defaultLookUpkey);
            if (defaultLookUpkey.isEmpty() == true) {
                throw new DataSourceLookUpException("Default Look Up key can not be Null or Empty, Please provide default lookup key in configuration file !!!");
            } else {
                return defaultLookUpkey.toString();
            }
        } else {
            return DBContextHolder.getDataBaseSite().toString();
        }
    }
}
