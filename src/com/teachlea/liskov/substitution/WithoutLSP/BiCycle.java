package com.teachlea.liskov.substitution.WithoutLSP;

public class BiCycle implements Bike{
    @Override
    public void turnOnEngine() {
        throw new AssertionError("I don't have an engine!"); // This violates the LSP as we are inherently changing the behavior of our program.
    }

    @Override
    public void accelerate() {
        /**
         * Code related to accelerate the BiCycle
         */
    }
}
