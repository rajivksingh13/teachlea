package com.teachlea.multidatasource.bean;

import lombok.Data;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;

@Data
@Entity
@Table(name = "countries")
public class countries {
    @Id
    public int id;
    public String name;
}
