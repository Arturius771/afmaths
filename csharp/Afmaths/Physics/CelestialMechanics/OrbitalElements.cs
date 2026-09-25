namespace Afmaths;

public class OrbitalElement(double value) : PhysicalValue(value)
{
}

public class MeanAnomaly(double value) : OrbitalElement(value)
{
}

public class EccentricAnomaly(double value) : OrbitalElement(value)
{
}

public class TrueAnomaly(double value) : OrbitalElement(value)
{
}

public class Eccentricity(double value) : OrbitalElement(value)
{
}

public class SemiMajorAxis(double value) : OrbitalElement(value)
{
}

public class Inclination(double value) : OrbitalElement(value)
{
}

public class RightAscensionAscendingNode(double value) : OrbitalElement(value)
{
}

public class ArgumentOfPeriapsis(double value) : OrbitalElement(value)
{
}



public class OrbitalElements(
        SemiMajorAxis semi_major_axis,
        Eccentricity eccentricity,
        Inclination inclination,
        RightAscensionAscendingNode right_ascension_of_ascending_node,
        ArgumentOfPeriapsis argument_of_periapsis,
        TrueAnomaly true_anomaly
    )
{
    public SemiMajorAxis SemiMajorAxis { get; } = semi_major_axis;
    public Eccentricity Eccentricity { get; } = eccentricity;
    public Inclination Inclination { get; } = inclination;
    public RightAscensionAscendingNode RightAscensionOfAscendingNode { get; } = right_ascension_of_ascending_node;
    public ArgumentOfPeriapsis ArgumentOfPeriapsis { get; } = argument_of_periapsis;
    public TrueAnomaly TrueAnomaly { get; } = true_anomaly;


    public Vector3D PerifocalRadialUnitVector()
    {
        return new Vector3D(
            Math.Cos(this.TrueAnomaly.Value),
            Math.Sin(this.TrueAnomaly.Value),
            0
        );
    }

    public Vector3D PerifocalVelocityDirection()
    {
        return new Vector3D(
            -Math.Sin(this.TrueAnomaly.Value),
            Math.Cos(this.TrueAnomaly.Value),
            0
        );
    }

}
