package com.teachlea.multidatasource.repository;

import com.teachlea.multidatasource.bean.countries;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CountryRepository extends JpaRepository<countries, Integer> {

    List<countries> findCountriesByname(String name);
}
