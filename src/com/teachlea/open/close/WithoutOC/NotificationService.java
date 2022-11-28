package com.teachlea.open.close.WithoutOC;

/**
 * NotificationService class is only sending OTP Notifications via sms and email. And this is Working Code in Production
 * If in Future there is Requirement to send OTP Notifications via whatsapp then its Voilates the OPEN-CLOSE preclinical
 * Which says Open For Extension but Close for Modifications
 */
public class NotificationService {

    public String sendOTP(String medium){

        if(medium.equalsIgnoreCase("sms")){
            /**
             * Code related to Send OTP through SMS
             */
        }
        if(medium.equalsIgnoreCase("email")){
            /**
             * Code related to Send OTP through email
             */
        }
        return "otp";
    }
}
