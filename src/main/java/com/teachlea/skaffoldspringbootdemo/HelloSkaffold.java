package com.teachlea.skaffoldspringbootdemo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloSkaffold {

    @GetMapping("/hello")
    public String getMessage(){
        return "Hello From Skaffold HOT BUILD DEPLOY PUSH of Spring Boot";
    }
}
