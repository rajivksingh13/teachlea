package com.teachlea.gradlejibdemo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloJibController {

    @GetMapping("/hello")
    public String getMessage(){
        return "Hello From Docker Image Created using Gradle Jib Plugin";
    }

    @GetMapping("/helloAWS")
    public String getAWSMessage(){
        return "Hello From Spring Boot Docker Container in AWS EC2";
    }
}
