package com.teachlea.mavenjibdemo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloJibController {

    @GetMapping("/hello")
    public String getMessage(){
        return "Hello From Docker Image Created using Maven Jib Plugin";
    }
}
