namespace Afmaths;

public class Manoeuvre
{
    public Orbit OriginalOrbit { get; }
    public Manoeuvre(Orbit orbit)
    {
        OriginalOrbit = orbit;
    }

    /// <summary>
    /// Calculates the phase orbit required to reach the target true anomaly.
    /// </summary>
    /// <param name="target">Target true anomaly to reach</param>
    /// <param name="mu">Gravitational parameter of the central body</param>
    /// <returns>Phase orbit as an Orbit object</returns>
    public Orbit PhaseOrbit(
        TrueAnomaly target,
        GravitationalParameter mu
    )
    {
        return new Orbit(
            new OrbitalElements(
                new OrbitalPeriod(
                    OriginalOrbit.Elements.SemiMajorAxis
                        .OrbitalPeriod(mu).ToTime()
                        .Delta(
                            OriginalOrbit.Elements.SemiMajorAxis
                                .DurationToReachTargetEccentricAnomaly(
                                    target
                                        .Delta(OriginalOrbit.Elements.TrueAnomaly)
                                        .ToEccentricAnomaly(
                                            OriginalOrbit.Elements.Eccentricity,
                                            false
                                        ),
                                    mu,
                                    OriginalOrbit.Elements.Eccentricity
                                )
                        )
                        .Value
                ).ToSemiMajorAxis(mu),
                OriginalOrbit.Elements.Eccentricity,
                OriginalOrbit.Elements.Inclination,
                OriginalOrbit.Elements.RightAscensionOfAscendingNode,
                OriginalOrbit.Elements.ArgumentOfPeriapsis,
                OriginalOrbit.Elements.TrueAnomaly
            ),
            mu
        );
    }

    public Velocity InclinationChangeDeltaV(Inclination target, Velocity atNode)
    {
        return new Velocity(2 * atNode.VectorMagnitude() * Math.Sin(OriginalOrbit.Elements.Inclination.Delta(target).Value / 2));
    }
}