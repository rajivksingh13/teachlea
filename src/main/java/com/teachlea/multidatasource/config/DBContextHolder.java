package com.teachlea.multidatasource.config;

public class DBContextHolder {

    private static final ThreadLocal<String> dataBaseSitesHolder = new ThreadLocal<>();

    public static void setDataBaseSite(String dataBaseSites) {
        dataBaseSitesHolder.set(dataBaseSites);
    }

    static String getDataBaseSite() {
        return dataBaseSitesHolder.get();
    }

    static void clear() {
        dataBaseSitesHolder.remove();
    }
}
