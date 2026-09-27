namespace Afmaths;

/// <summary>
/// Represents a physical value with a double precision floating point number.
/// </summary>
public abstract class PhysicalValue<TSelf>
    where TSelf : PhysicalValue<TSelf>
{
    public double Value { get; }

    protected PhysicalValue(double value)
    {
        Value = value;
    }

    protected abstract TSelf Create(double value);

    /// <summary>
    /// Normalizes the value to the range [0, 2π) radians.
    /// </summary>
    /// <returns>The normalized physical value in the range [0, 2π) radians</returns>
    public TSelf NormalizeRadians()
    {
        var normalized = Value % (2 * Math.PI);

        if (normalized < 0)
            normalized += 2 * Math.PI;

        return Create(normalized);
    }

    /// <summary>
    /// Calculates the difference between this physical value and another.
    /// </summary>
    /// <param name="other">The other physical value to compare with</param>
    /// <returns>The difference between this physical value and the other</returns>
    public TSelf Delta(TSelf other)
    {
        ArgumentNullException.ThrowIfNull(other);
        return Create(Value - other.Value);
    }
}

/// <summary>
/// Represents a mass value in kilograms.
/// </summary>
public class Mass(double value) : PhysicalValue<Mass>(value)
{
    /// <summary>
    /// Represents the mass of the Earth in kilograms.
    /// </summary>
    public static readonly Mass EarthMass = new Mass(5.972e24);
    /// <summary>
    /// Represents the mass of the Sun in kilograms.
    /// </summary>
    public static readonly Mass SunMass = new Mass(1.989e30);
    /// <summary>
    /// Represents the mass of a proton in kilograms.
    /// </summary>
    public static readonly Mass ProtonMass = new Mass(1.6726219e-27);
    /// <summary>
    /// Represents the mass of a demo satellite in kilograms.
    /// </summary>
    public static readonly Mass DemoSatelliteMass = new Mass(1.0e3);


    protected override Mass Create(double value) => new(value);
}


public class Rate(double value) : PhysicalValue<Rate>(value)
{
    protected override Rate Create(double value) => new(value);
}

public class AngularMomentum(Vector3D<double> value) : Vector3D<double>(value.X, value.Y, value.Z)
{
}