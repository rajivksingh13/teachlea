package com.teachlea.dependency.injection.WithoutDI;

public class Windows98Machine {
    private final StandardKeyboard keyboard;
    private final Monitor monitor;

    public Windows98Machine() {
        monitor = new Monitor();        // By declaring the StandardKeyboard and Monitor with the new keyword, we've tightly coupled these three classes together
        keyboard = new StandardKeyboard();
    }
}
