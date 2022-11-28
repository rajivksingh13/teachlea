package com.teachlea.inteface.segregation.WithoutIS;

/**
 * This Class violates IS principle as it needs to  washDishes() and cookFood() method which is not a Waiter's Job
 */
public class Waiter implements ResturantEmployee{

    // This method is not Required for Waiter
    @Override
    public void washDishes() {

    }

    @Override
    public void takeOrder() {

    }

    @Override
    public void serveFood() {

    }

    // This method is not Required for Waiter
    @Override
    public void cookFood() {

    }
}
