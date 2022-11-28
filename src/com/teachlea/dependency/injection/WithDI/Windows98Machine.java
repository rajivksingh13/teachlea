package com.teachlea.dependency.injection.WithDI;

import com.teachlea.dependency.injection.WithoutDI.Monitor;

/**
 * Now our classes are decoupled and communicate through the Keyboard abstraction.
 * If we want, we can easily switch out the type of keyboard in our machine with a different implementation of the interface.
 * Same applies for Monitor as well
 */
public class Windows98Machine {
    private final KeyBoard keyboard;
    private final Monitor monitor;

    public Windows98Machine(KeyBoard keyboard, Monitor monitor) {
        this.keyboard = keyboard;
        this.monitor = monitor;
    }
}
