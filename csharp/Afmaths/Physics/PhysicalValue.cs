namespace Afmaths;

public class PhysicalValue
{
    public double Value { get; }

    public PhysicalValue(double value)
    {
        Value = value;
    }
}


public class Mass(double value) : PhysicalValue(value)
{
    public static readonly Mass EarthMass = new Mass(5.972e24);
    public static readonly Mass SunMass = new Mass(1.989e30);
    public static readonly Mass ProtonMass = new Mass(1.6726219e-27);
    public static readonly Mass DemoSatelliteMass = new Mass(1.0e3);
}