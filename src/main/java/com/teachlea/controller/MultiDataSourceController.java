package com.teachlea.controller;

import com.teachlea.bean.Country;
import io.agroal.api.AgroalDataSource;
import io.quarkus.agroal.DataSource;

import javax.inject.Inject;
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

@Path("/hello")
public class MultiDataSourceController {
    @Inject
    AgroalDataSource defaultDataSource;

    @Inject
    @DataSource("mysqldb")
    AgroalDataSource mysqlDataSource;

    @Inject
    @DataSource("mymaria")
    AgroalDataSource mariaDataSource;

    @GET()
    @Path("/postgres/countries")
    @Produces(MediaType.APPLICATION_JSON)
    public List<Country> getAllCountries() throws SQLException {
        List<Country> countries = new ArrayList<Country>();
        Connection connection = null;
        Statement statement = null;
        ResultSet resultSet = null;
        try {
            connection = defaultDataSource.getConnection();
            statement = connection.createStatement();
            resultSet = statement.executeQuery("select * from countries;");
            while (resultSet.next()) {
                Country country = new Country();
                country.setId(resultSet.getInt("id"));
                country.setName(resultSet.getString("name"));
                countries.add(country);
            }
        } finally {
            if (resultSet != null) try {
                resultSet.close();
            } catch (SQLException ignore) {
            }
            if (statement != null) try {
                statement.close();
            } catch (SQLException ignore) {
            }
            if (connection != null) try {
                connection.close();
            } catch (SQLException ignore) {
            }
        }
        return countries;
    }

    @GET()
    @Path("/maria/countries")
    @Produces(MediaType.APPLICATION_JSON)
    public List<Country> getAllMariaCountries() throws SQLException {
        List<Country> countries = new ArrayList<Country>();
        Connection connection = null;
        Statement statement = null;
        ResultSet resultSet = null;
        try {
            connection = mariaDataSource.getConnection();
            statement = connection.createStatement();
            resultSet = statement.executeQuery("select * from countries;");
            while (resultSet.next()) {
                Country country = new Country();
                country.setId(resultSet.getInt("id"));
                country.setName(resultSet.getString("name"));
                countries.add(country);
            }
        } finally {
            if (resultSet != null) try {
                resultSet.close();
            } catch (SQLException ignore) {
            }
            if (statement != null) try {
                statement.close();
            } catch (SQLException ignore) {
            }
            if (connection != null) try {
                connection.close();
            } catch (SQLException ignore) {
            }
        }
        return countries;
    }

    @GET()
    @Path("/mysql/countries")
    @Produces(MediaType.APPLICATION_JSON)
    public List<Country> getAllMysqlCountries() throws SQLException {
        List<Country> countries = new ArrayList<Country>();
        Connection connection = null;
        Statement statement = null;
        ResultSet resultSet = null;
        try {
            connection = mysqlDataSource.getConnection();
            statement = connection.createStatement();
            resultSet = statement.executeQuery("select * from countries;");
            while (resultSet.next()) {
                Country country = new Country();
                country.setId(resultSet.getInt("id"));
                country.setName(resultSet.getString("name"));
                countries.add(country);
            }
        } finally {
            if (resultSet != null) try {
                resultSet.close();
            } catch (SQLException ignore) {
            }
            if (statement != null) try {
                statement.close();
            } catch (SQLException ignore) {
            }
            if (connection != null) try {
                connection.close();
            } catch (SQLException ignore) {
            }
        }

        return countries;
    }
}
