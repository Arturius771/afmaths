namespace Afmaths;

/// <summary>
/// Represents a generic orbital element, which is a parameter that defines the characteristics of an orbit.
/// </summary>
/// <typeparam name="T">The type of the orbital element.</typeparam>
/// <param name="value">The value of the orbital element.</param>
public abstract class OrbitalElement<T>(double value)
    : PhysicalValue<T>(value)
    where T : OrbitalElement<T>
{
    public Distance AsDistance()
    {
        return new Distance(Value);
    }
}

/// <summary>
/// Represents a generic orbital anomaly, which is an angular parameter that describes the position of a body along its orbit.
/// </summary>
/// <typeparam name="T">The type of the orbital anomaly.</typeparam>
/// <param name="value">The value of the orbital anomaly.</param>
public abstract class Anomaly<T>(double value)
    : OrbitalElement<T>(value)
    where T : Anomaly<T>
{
}

/// <summary>
/// Mean Anomaly is the angular parameter that represents the fraction
/// of an orbital period that has elapsed since the last periapsis passage,
/// expressed as an angle.
/// </summary>
/// <param name="value">The value of the mean anomaly.</param>
public class MeanAnomaly(double value)
    : Anomaly<MeanAnomaly>(value)
{
    public MeanAnomaly AtTime(
        Time offset,
        MeanMotion n
    )
    {
        return new MeanAnomaly(
            Value + n.Value * offset.Value
        );
    }

    public Time SincePeriapsis(
        OrbitalPeriod p
    )
    {
        return new Time(
            p.Value
            * new Ratio(
                Value,
                2 * Math.PI
            ).Value
        );
    }


    protected override MeanAnomaly Create(double value) => new(value);
}

/// <summary>
/// Represents the eccentric anomaly orbital element.
/// </summary>
/// <param name="value">The value of the eccentric anomaly.</param>
public class EccentricAnomaly(double value)
    : Anomaly<EccentricAnomaly>(value)
{
    private readonly NumericalAnalysis numericalAnalysis = new();
    private readonly CelestialMechanics celestialMechanics = new();

    private EccentricAnomaly NewtonMethodIteration(
        EccentricAnomaly guess,
        Eccentricity eccentricity,
        MeanAnomaly meanAnomaly
    )
    {
        return new EccentricAnomaly(
            numericalAnalysis.NewtonRaphson(
                guess.Value,
                celestialMechanics
                    .KeplerEquation(
                        guess,
                        eccentricity
                    )
                    .Value
                - meanAnomaly.Value,
                1
                - eccentricity.Value
                * Math.Cos(guess.Value)
            )
        );
    }

    public (
        EccentricAnomaly EccentricAnomaly,
        History<EccentricAnomaly> History
    ) NewtonMethod(
        Eccentricity eccentricity,
        MeanAnomaly meanAnomaly
    )
    {
        return numericalAnalysis.RootSolver(
            initialGuess =>
                NewtonMethodIteration(
                    initialGuess,
                    eccentricity,
                    meanAnomaly
                ),
            this,
            (next, current) =>
                next.Value - current.Value
        );
    }

    public TrueAnomaly ToTrueAnomaly(
        Eccentricity eccentricity
    )
    {
        return new TrueAnomaly(
            Math.Atan2(
                Math.Sqrt(
                    1
                    - Math.Pow(
                        eccentricity.Value,
                        2
                    )
                )
                * Math.Sin(Value),
                Math.Cos(Value)
                - eccentricity.Value
            )
        ).NormalizeRadians();
    }


    protected override EccentricAnomaly Create(double value) => new(value);
}

/// <summary>
/// Represents the mean motion orbital element. This is also known as the mean angular rate.
/// </summary>
/// <param name="value">The value of the mean motion.</param>
public class MeanMotion(double value)
    : OrbitalElement<MeanMotion>(value)
{
    public OrbitalPeriod OrbitalPeriod()
    {
        return new OrbitalPeriod(
            2 * Math.PI / Value
        );
    }

    /// <summary>
    /// Represents the mean angular rate (mean motion) of the orbit.
    /// </summary>
    /// <returns>The mean angular rate of the orbit.</returns>
    public Rate MeanAngularRate()
    {
        return new Rate(Value);
    }


    protected override MeanMotion Create(double value) => new(value);
}

public class TrueAnomaly(double value)
    : Anomaly<TrueAnomaly>(value)
{
    /// <summary>
    /// Converts the true anomaly to the corresponding eccentric anomaly.
    /// </summary>
    /// <param name="eccentricity">Eccentricity of the orbit</param>
    /// <param name="normalize">Whether to normalize the resulting eccentric anomaly to the range [0, 2π)</param>
    /// <returns>Eccentric anomaly corresponding to the true anomaly</returns>
    public EccentricAnomaly ToEccentricAnomaly(
        Eccentricity eccentricity,
        bool normalize = true
    )
    {
        var result = new EccentricAnomaly(
            Math.Atan2(
                Math.Sqrt(
                    1
                    - eccentricity.Value
                    * eccentricity.Value
                )
                * Math.Sin(Value),
                eccentricity.Value
                + Math.Cos(Value)
            )
        );

        return normalize
            ? result.NormalizeRadians()
            : result;
    }

    public TrueAnomaly AtTime(
        Eccentricity eccentricity,
        MeanAnomaly meanAnomaly,
        Time offset,
        MeanMotion n
    )
    {
        return ToEccentricAnomaly(eccentricity)
            .NewtonMethod(
                eccentricity,
                meanAnomaly.AtTime(
                    offset,
                    n
                )
            )
            .EccentricAnomaly
            .ToTrueAnomaly(eccentricity);
    }

    public new TrueAnomaly Delta(
        TrueAnomaly other
    )
    {
        double delta =
            Value - other.Value;

        if (delta > Math.PI)
        {
            delta -= 2 * Math.PI;
        }
        else if (delta < -Math.PI)
        {
            delta += 2 * Math.PI;
        }

        return new TrueAnomaly(delta);
    }


    protected override TrueAnomaly Create(double value) => new(value);
}

public class Eccentricity(double value)
    : OrbitalElement<Eccentricity>(value)
{

    protected override Eccentricity Create(double value) => new(value);
}

/// <summary>
/// Semi-major axis is the longest radius of an elliptical orbit,
/// representing half of the major axis.
/// </summary>
/// <param name="value">The value of the semi-major axis.</param>
public class SemiMajorAxis(double value)
    : OrbitalElement<SemiMajorAxis>(value)
{
    /// <summary>
    /// Calculates the mean motion (mean angular rate) of the orbit based on the semi-major axis and the gravitational parameter.
    /// </summary>
    /// <param name="mu">The standard gravitational parameter of the central body</param>
    /// <returns>The mean motion (mean angular rate) of the orbit</returns>
    public MeanMotion ToMeanMotion(
        GravitationalParameter mu
    )
    {
        // n = sqrt(mu / a^3)
        return new MeanMotion(Math.Sqrt(mu.Value / Math.Pow(Value, 3)));
    }

    /// <summary>
    /// Calculates the orbital period of the orbit based on the semi-major axis and the gravitational parameter.
    /// </summary>
    /// <param name="mu">The standard gravitational parameter of the central body</param>
    /// <returns>The orbital period of the orbit</returns>
    public OrbitalPeriod OrbitalPeriod(
        GravitationalParameter mu
    )
    {
        // T = 2 * pi * sqrt(a^3 / mu)
        return new OrbitalPeriod(2 * Math.PI * Math.Sqrt(Math.Pow(Value, 3) / mu.Value));
    }

    /// <summary>
    /// Calculates the duration required to reach a specific target eccentric anomaly in the orbit.
    /// </summary>
    /// <param name="target">The target eccentric anomaly to reach</param>
    /// <param name="mu">The standard gravitational parameter of the central body</param>
    /// <param name="eccentricity">The eccentricity of the orbit</param>
    /// <returns>The time required to reach the target eccentric anomaly from periapsis</returns>
    public Time DurationToReachTargetEccentricAnomaly(
        EccentricAnomaly target,
        GravitationalParameter mu,
        Eccentricity eccentricity
    )
    {
        return new CelestialMechanics()
            .KeplerEquation(
                target,
                eccentricity
            )
            .SincePeriapsis(
                OrbitalPeriod(mu)
            );
    }


    protected override SemiMajorAxis Create(double value) => new(value);
}

/// <summary>
/// Represents the inclination of an orbit, which is the angle between
/// the orbital plane and the reference plane.
/// </summary>
public class Inclination(double value)
    : OrbitalElement<Inclination>(value)
{

    protected override Inclination Create(double value) => new(value);
}

/// <summary>
/// Represents the right ascension of the ascending node of an orbit, which is the angle between
/// the reference direction and the ascending node of the orbit.
/// </summary>
/// <param name="value">The value of the right ascension of the ascending node</param>
public class RightAscensionAscendingNode(double value)
    : OrbitalElement<RightAscensionAscendingNode>(value)
{
    protected override RightAscensionAscendingNode Create(double value) => new(value);
}

/// <summary>
/// Represents the argument of periapsis of an orbit, which is the angle between the ascending node and the periapsis within the orbital plane.
/// </summary>
/// <param name="value">The value of the argument of periapsis</param>
public class ArgumentOfPeriapsis(double value)
    : OrbitalElement<ArgumentOfPeriapsis>(value)
{
    protected override ArgumentOfPeriapsis Create(double value) => new(value);
}

/// <summary>
/// Represents the semi-minor axis of an orbit, which is the shortest radius of the ellipse.
/// </summary>
/// <param name="value">The value of the semi-minor axis</param>
public class SemiMinorAxis(double value)
    : OrbitalElement<SemiMinorAxis>(value)
{
    protected override SemiMinorAxis Create(double value) => new(value);
}

/// <summary>
/// Represents the semi-latus rectum of an orbit, which is the distance from the focus to the orbit at the orbit's closest approach perpendicular to the major axis.
/// </summary>
/// <param name="value">The value of the semi-latus rectum</param>
public class SemiLatusRectum(double value)
    : OrbitalElement<SemiLatusRectum>(value)
{
    protected override SemiLatusRectum Create(double value) => new(value);

    public SemiMinorAxis ToSemiMinorAxis(
        SemiMajorAxis a
    )
    {
        return new SemiMinorAxis(
            new EuclidianDistance()
                .GeometricMeanDistance(
                    a.AsDistance(),
                    AsDistance()
                )
                .Value
        );
    }
}

/// <summary>
/// Represents the orbital period of an orbit, which is the time taken for a body to complete one full orbit around the central body.
/// </summary>
/// <param name="value">The value of the orbital period</param>
public class OrbitalPeriod(double value)
    : OrbitalElement<OrbitalPeriod>(value)
{
    /// <summary>
    /// Converts the orbital period to the corresponding semi-major axis using Kepler's third law.
    /// </summary>
    /// <param name="mu">The standard gravitational parameter of the central body</param>
    /// <returns>The semi-major axis corresponding to the orbital period</returns>
    /// <remarks>
    /// This method assumes a two-body system and uses Kepler's third law to relate the orbital period to the semi-major axis.
    /// </remarks>
    public SemiMajorAxis ToSemiMajorAxis(
        GravitationalParameter mu
    )
    {
        return new SemiMajorAxis(
            Math.Pow(
                Math.Sqrt(mu.Value)
                * Value
                / (2 * Math.PI),
                2.0 / 3.0
            )
        );
    }

    /// <summary>
    /// Converts the orbital period to a time value.
    /// </summary>
    /// <returns>The time value corresponding to the orbital period</returns>
    public Time ToTime()
    {
        return new Time(Value);
    }


    protected override OrbitalPeriod Create(double value) => new(value);

    // public Time Delta(
    //     Time other
    // )
    // {
    //     return new Time(
    //         Value - other.Value
    //     );
    // }
}

/// <summary>
/// Represents the set of orbital elements defining an orbit.
/// </summary>
/// <param name="argumentOfPeriapsis">The argument of periapsis of the orbit</param>
/// <param name="semiMajorAxis">The semi-major axis of the orbit</param>
/// <param name="eccentricity">The eccentricity of the orbit</param>
/// <param name="inclination">The inclination of the orbit</param>
/// <param name="rightAscensionOfAscendingNode">The right ascension of the ascending node of the orbit</param>
/// <param name="trueAnomaly">The true anomaly of the orbit</param>
public class OrbitalElements(
    SemiMajorAxis semiMajorAxis,
    Eccentricity eccentricity,
    Inclination inclination,
    RightAscensionAscendingNode rightAscensionOfAscendingNode,
    ArgumentOfPeriapsis argumentOfPeriapsis,
    TrueAnomaly trueAnomaly
)
{
    public SemiMajorAxis SemiMajorAxis { get; } =
        semiMajorAxis;

    public Eccentricity Eccentricity { get; } =
        eccentricity;

    public Inclination Inclination { get; } =
        inclination;

    public RightAscensionAscendingNode RightAscensionOfAscendingNode { get; } =
        rightAscensionOfAscendingNode;

    public ArgumentOfPeriapsis ArgumentOfPeriapsis { get; } =
        argumentOfPeriapsis;

    public TrueAnomaly TrueAnomaly { get; } =
        trueAnomaly;

    /// <summary>
    /// Returns the perifocal radial unit vector.
    /// </summary>
    public Vector3D<double> PerifocalRadialUnitVector()
    {
        return new Vector3D<double>(
            Math.Cos(TrueAnomaly.Value),
            Math.Sin(TrueAnomaly.Value),
            0
        );
    }

    /// <summary>
    /// Returns the tangential perifocal direction vector.
    /// </summary>
    public Vector3D<double> PerifocalVelocityDirection()
    {
        return new Vector3D<double>(
            -Math.Sin(TrueAnomaly.Value),
            Math.Cos(TrueAnomaly.Value),
            0
        );
    }
}