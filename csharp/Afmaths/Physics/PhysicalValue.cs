namespace Afmaths;

/// <summary>
/// Represents a physical value with a double precision floating point number.
/// </summary>
public class PhysicalValue
{
    public double Value { get; }

    public PhysicalValue(double value)
    {
        Value = value;
    }


    /// <summary>
    /// Normalizes the value to the range [0, 2π) and returns a new instance of the specified type.
    /// </summary>
    public T NormalizeRadians<T>() where T : PhysicalValue
    {
        double normalizedValue = Value % (2 * Math.PI);

        if (normalizedValue < 0)
        {
            normalizedValue += 2 * Math.PI;
        }

        return (T)(Activator.CreateInstance(typeof(T), normalizedValue)
            ?? throw new InvalidOperationException($"Could not create an instance of {typeof(T)}."));
    }
}

/// <summary>
/// Represents a mass value in kilograms.
/// </summary>
public class Mass(double value) : PhysicalValue(value)
{
    public static readonly Mass EarthMass = new Mass(5.972e24);
    public static readonly Mass SunMass = new Mass(1.989e30);
    public static readonly Mass ProtonMass = new Mass(1.6726219e-27);
    public static readonly Mass DemoSatelliteMass = new Mass(1.0e3);
}

/// <summary>
/// Represents a time value in seconds.
/// </summary>
public class Time(double value) : PhysicalValue(value)
{
}

public class Rate(double value) : PhysicalValue(value)
{
}