package com.teachlea.single.responsiblity.WithoutSR;

/**
 * This class violates the Single Responsibility Principal
 * As methods deposit(), withdraw(), sendOTP() and printPassbook() are not related to Account Creation or Account Close.
 * BankAccount class should be only Responsible to do any Changes w.r.t. BankAccount Creation or Close
 * If in future we get some use-case to change the Deposit, Withdraw, Notification using OTP or Printing PassBook related Business use-case then in that case
 * We need to make the modification to BankAccount class
 *
 */
public class BankAccount {

      // Create Bank Account
    public void createBankAccount(){
        /**
         * Code related to create a Bank Account
         */
    }
    // Close Bank Account
    public void closeBankAccount(){
        /**
         * Code related to close a Bank Account
         */
    }

    // Deposit Money to Bank Account
    public void deposit(){
        /**
         * Code related to Deposit Money to Bank Account
         */
    }

    // Withdraw Money from Bank Account
    public void withdraw(){
        /**
         * Code related to Withdraw Money to Bank Account
         */
    }
    // Send OTP Notifications
    public String sendOTP(){
        /**
         * Code related to Send the OTP Notification
         */
        return "otp";
    }
    // Print PassBooks
    public void printPassbook(){
        /**
         * Code related to Printing PassBooks
         */
    }
}
