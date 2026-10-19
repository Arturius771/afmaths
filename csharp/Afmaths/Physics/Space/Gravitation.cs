namespace Afmaths;

public class GravitationalConstant
{
    public double Value { get; }

    public GravitationalConstant()
    {
        Value = 6.67430e-11;
    }
}

/// <summary>
/// Represents the standard gravitational parameter (μ) of a celestial body, which is the product of the gravitational constant and the mass of the body.
/// </summary>
/// <param name="value">The value of the standard gravitational parameter (μ) in m^3/s^2.</param>
public class GravitationalParameter(double value) : PhysicalValue<GravitationalParameter>(value)
{

    public static readonly GravitationalParameter EarthGravitationalParameter = FromMasses(
        Mass.EarthMass,
        Mass.DemoSatelliteMass
    );

    public static readonly GravitationalParameter SunGravitationalParameter = FromMasses(
        Mass.SunMass,
        Mass.EarthMass
    );

    public static GravitationalParameter FromMasses(
        Mass central,
        Mass orbiting
    )
    {
        var value =
            new GravitationalConstant().Value
            * (central.Value + orbiting.Value);

        return new GravitationalParameter(value);
    }

    protected override GravitationalParameter Create(double value) => new(value);
}