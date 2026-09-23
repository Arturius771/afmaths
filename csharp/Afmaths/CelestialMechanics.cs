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
    MeanAnomaly mean_anomaly
)
{
    public SemiMajorAxis SemiMajorAxis { get; } = semi_major_axis;
    public Eccentricity Eccentricity { get; } = eccentricity;
    public Inclination Inclination { get; } = inclination;
    public RightAscensionAscendingNode RightAscensionOfAscendingNode { get; } = right_ascension_of_ascending_node;
    public ArgumentOfPeriapsis ArgumentOfPeriapsis { get; } = argument_of_periapsis;
    public MeanAnomaly MeanAnomaly { get; } = mean_anomaly;
}




public class CelestialMechanics
{

    public MeanAnomaly KeplerEquation(EccentricAnomaly eccentric_anomaly, Eccentricity eccentric)
    {
        // M = E - e * np.sin(E)
        return new MeanAnomaly(
            eccentric_anomaly.Value - eccentric.Value * Math.Sin(eccentric_anomaly.Value)
        );
    }

    public Velocity VisViva(GravitationalParameter mu, Distance radius, SemiMajorAxis a)
    {
        // v = sqrt(mu * (2/r - 1/a))
        return new Velocity(
            Math.Sqrt(mu.Value * (2 / radius.Value - 1 / a.Value))
        );
    }

    public Distance OrbitEquation(SemiMajorAxis a, Eccentricity e, TrueAnomaly theta)
    {
        // r = a * (1 - e^2) / (1 + e * cos(theta))
        return new Distance(
            a.Value * (1 - e.Value * e.Value) / (1 + e.Value * Math.Cos(theta.Value))
        );
    }

}
