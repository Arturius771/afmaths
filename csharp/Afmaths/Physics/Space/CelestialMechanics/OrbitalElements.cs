namespace Afmaths;

public abstract class OrbitalElement(double value) : PhysicalValue(value)
{

    public Distance AsDistance()
    {
        return new Distance(this.Value);
    }
}

/// <summary>
/// Mean Anomaly is the angular parameter that represents the fraction of an orbital period that has elapsed since the last periapsis passage, expressed as an angle.
/// </summary>
/// <param name="value">The value of the mean anomaly.</param>
public class MeanAnomaly(double value) : OrbitalElement(value)
{
    public MeanAnomaly AtTime(Time offset, MeanMotion n)
    {
        return new MeanAnomaly(this.Value + n.Value * offset.Value);
    }
}

/// <summary>
/// Represents the eccentric anomaly orbital element. The eccentric anomaly is an angular parameter that describes the position of a body in its elliptical orbit as a function of time.
/// </summary>
/// <param name="value">The value of the eccentric anomaly.</param>
public class EccentricAnomaly(double value) : OrbitalElement(value)
{
    NumericalAnalysis numericalAnalysis = new NumericalAnalysis();
    CelestialMechanics celestialMechanics = new CelestialMechanics();

    //eccentric anomaly solved using root solver
    EccentricAnomaly NewtonMethodIteration(EccentricAnomaly guess, Eccentricity eccentricity, MeanAnomaly mean_anomaly)
    {
        return new EccentricAnomaly(numericalAnalysis.NewtonRaphson(
            guess.Value,
            celestialMechanics.KeplerEquation(guess, eccentricity).Value - mean_anomaly.Value,
            1 - eccentricity.Value * Math.Cos(guess.Value)
        ));
    }

    public (EccentricAnomaly EccentricAnomaly, History<EccentricAnomaly> History) NewtonMethod(Eccentricity eccentricity, MeanAnomaly mean_anomaly)
    {
        return numericalAnalysis.RootSolver(
            (initial_guess) => this.NewtonMethodIteration(initial_guess, eccentricity, mean_anomaly),
            this,
            (next, current) => next.Value - current.Value
        );
    }

    public TrueAnomaly ToTrueAnomaly(Eccentricity eccentricity)
    {
        return new TrueAnomaly(
            Math.Atan2(Math.Sqrt(1 - Math.Pow(eccentricity.Value, 2)) * Math.Sin(this.Value), Math.Cos(this.Value) - eccentricity.Value)).NormalizeRadians<TrueAnomaly>();
    }
}

public class MeanMotion(double value) : OrbitalElement(value)
{
}

public class TrueAnomaly(double value) : OrbitalElement(value)
{
    public EccentricAnomaly ToEccentricAnomaly(Eccentricity eccentricity)
    {
        return new EccentricAnomaly(
            Math.Acos((Math.Cos(this.Value) + eccentricity.Value) / (1 + eccentricity.Value * Math.Cos(this.Value)))
        );
    }

    public TrueAnomaly AtTime(Eccentricity eccentricity, MeanAnomaly mean_anomaly, Time offset, MeanMotion n)
    {
        return this.ToEccentricAnomaly(eccentricity).NewtonMethod(eccentricity, mean_anomaly.AtTime(offset, n)).EccentricAnomaly.ToTrueAnomaly(eccentricity);
    }
}

public class Eccentricity(double value) : OrbitalElement(value)
{
}

/// <summary>
/// Semi-major axis is the longest radius of an elliptical orbit, representing half of the major axis.
/// </summary>
/// <param name="value">The value of the semi-major axis.</param>
public class SemiMajorAxis(double value) : OrbitalElement(value)
{

    public MeanMotion ToMeanMotion(GravitationalParameter mu)
    {
        return new MeanMotion(new CelestialMechanics().MeanAngularRate(this, mu).Value);
    }
}

/// <summary>
/// Represents the inclination of an orbit, which is the angle between the orbital plane and the reference plane.
/// </summary>
public class Inclination(double value) : OrbitalElement(value)
{
}

public class RightAscensionAscendingNode(double value) : OrbitalElement(value)
{
}

public class ArgumentOfPeriapsis(double value) : OrbitalElement(value)
{
}

public class SemiMinorAxis(double value) : OrbitalElement(value)
{
}

public class SemiLatusRectum(double value) : OrbitalElement(value)
{

    public SemiMinorAxis ToSemiMinorAxis(SemiMajorAxis a)
    {
        return new SemiMinorAxis(new EuclidianDistance().GeometricMeanDistance(a.AsDistance(), this.AsDistance()).Value);
    }
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


    /// <summary>
    /// Returns the perifocal radial unit vector, which points from the central body to the orbiting body in the perifocal coordinate system.
    /// </summary>
    /// <returns>The perifocal radial unit vector as a 3D vector.</returns>
    public Vector3D<double> PerifocalRadialUnitVector()
    {
        return new Vector3D<double>(
            Math.Cos(this.TrueAnomaly.Value),
            Math.Sin(this.TrueAnomaly.Value),
            0
        );
    }

    /// <summary>
    /// Returns the perifocal velocity direction unit vector, which is perpendicular to the perifocal radial unit vector in the direction of motion.
    /// </summary>
    /// <returns>The perifocal velocity direction unit vector as a 3D vector.</returns>
    public Vector3D<double> PerifocalVelocityDirection()
    {
        return new Vector3D<double>(
            -Math.Sin(this.TrueAnomaly.Value),
            Math.Cos(this.TrueAnomaly.Value),
            0
        );
    }

}
