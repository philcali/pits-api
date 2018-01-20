package me.philcali.pits.data.model;

import java.util.Date;

public interface IDevice {
    String getId();
    Date getLastUpdate();
    String getMacAddress();
    ISystemInformation getSystemInformation();
    String getVersion();
}
