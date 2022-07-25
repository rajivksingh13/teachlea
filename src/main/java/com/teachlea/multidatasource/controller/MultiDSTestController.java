package com.teachlea.multidatasource.controller;

import com.teachlea.multidatasource.bean.countries;
import com.teachlea.multidatasource.config.DBContextHolder;
import com.teachlea.multidatasource.repository.CountryRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.ArrayList;
import java.util.List;

@RestController
@Slf4j
public class MultiDSTestController {

    @Autowired
    CountryRepository countryRepository;

    @GetMapping("/countries")
    public ResponseEntity<List<countries>> getAllCountries(@RequestParam(required = false) String name, @RequestParam(required = false) String client) {
        List<countries> countries = new ArrayList<countries>();
        try {
            switch (client) {
                case "mysqldb":
                case "mypostgrey":
                case "mymaria":
                    DBContextHolder.setDataBaseSite(client);
                    if (name == null) {
                        countryRepository.findAll().forEach(countries::add);
                    } else {
                        countryRepository.findCountriesByname(name).forEach(countries::add);
                    }
                    if (countries.isEmpty()) {
                        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
                    }
            }
        } catch (Exception e) {
            return new ResponseEntity<>(null, HttpStatus.INTERNAL_SERVER_ERROR);
        }
        return new ResponseEntity<>(countries, HttpStatus.OK);
    }

}
