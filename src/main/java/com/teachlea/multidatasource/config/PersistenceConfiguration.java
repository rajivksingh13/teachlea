package com.teachlea.multidatasource.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.orm.hibernate5.LocalSessionFactoryBean;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;
import org.springframework.orm.jpa.vendor.HibernateJpaVendorAdapter;
import org.springframework.transaction.PlatformTransactionManager;
import javax.sql.DataSource;
import java.util.Properties;

@Configuration
@EnableJpaRepositories(basePackages = "com.*",
        entityManagerFactoryRef = "multiEntityManager",
        transactionManagerRef = "multiTransactionManager")
public class PersistenceConfiguration {

    @Autowired
    DataBaseConfig dataBaseConfig;
    private final String PACKAGE_SCAN = "com.*";

    @Bean
    DataSource multiRoutingDataSource() {
        MultiRoutingDataSource dataSource = new MultiRoutingDataSource();
        dataSource.setTargetDataSources(dataBaseConfig.createTargetDataSources());
        return dataSource;
    }

    @Bean
    LocalContainerEntityManagerFactoryBean multiEntityManager() {
        LocalContainerEntityManagerFactoryBean em = new LocalContainerEntityManagerFactoryBean();
        em.setDataSource(multiRoutingDataSource());
        em.setPackagesToScan(PACKAGE_SCAN);
        HibernateJpaVendorAdapter vendorAdapter = new HibernateJpaVendorAdapter();
        em.setJpaVendorAdapter(vendorAdapter);
        em.setJpaProperties(hibernateProperties());
        return em;
    }
    @Bean
    PlatformTransactionManager multiTransactionManager() {
        JpaTransactionManager transactionManager = new JpaTransactionManager();
        transactionManager.setEntityManagerFactory(
                multiEntityManager().getObject());
        return transactionManager;
    }

    LocalSessionFactoryBean dbSessionFactory() {
        LocalSessionFactoryBean sessionFactoryBean = new LocalSessionFactoryBean();
        sessionFactoryBean.setDataSource(multiRoutingDataSource());
        sessionFactoryBean.setPackagesToScan(PACKAGE_SCAN);
        sessionFactoryBean.setHibernateProperties(hibernateProperties());
        return sessionFactoryBean;
    }
    private Properties hibernateProperties() {
        Properties properties = new Properties();
        properties.put("hibernate.show_sql", true);
        properties.put("hibernate.format_sql", true);
        properties.put("hibernate.dialect", "org.hibernate.dialect.MySQL5InnoDBDialect");
        return properties;
    }
}
