namespace Afmaths;



public class CelestialMechanics
{
    public MeanAnomaly KeplerEquation(EccentricAnomaly eccentric_anomaly, Eccentricity eccentricity)
    {
        // M = E - e * np.sin(E)
        return new MeanAnomaly(
            eccentric_anomaly.Value - eccentricity.Value * Math.Sin(eccentric_anomaly.Value)
        );
    }

    /// <summary>
    /// Calculates the orbital velocity of a body at a given distance from the central body using the vis-viva equation.
    /// </summary>
    /// <param name="mu">The standard gravitational parameter of the central body.</param>
    /// <param name="radius">The distance of the orbiting body from the central body.</param>
    /// <param name="a">The semi-major axis of the orbit.</param>
    /// <returns>The orbital velocity of the body at the given distance.</returns>
    public Velocity VisViva(GravitationalParameter mu, Distance radius, SemiMajorAxis a)
    {
        // v = sqrt(mu * (2/r - 1/a))
        return new Velocity(
            Math.Sqrt(mu.Value * (2 / radius.Value - 1 / a.Value))
        );
    }

    /// <summary>
    /// Calculates the distance of a body from the central body at a given true anomaly using the orbit equation.
    /// </summary>
    /// <param name="a">The semi-major axis of the orbit.</param>
    /// <param name="e">The eccentricity of the orbit.</param>
    /// <param name="theta">The true anomaly of the orbiting body.</param>
    /// <returns>The distance of the body from the central body at the given true anomaly.</returns>
    public Distance OrbitEquation(SemiMajorAxis a, Eccentricity e, TrueAnomaly theta)
    {
        // r = a * (1 - e^2) / (1 + e * cos(theta))
        return new Distance(
            a.Value * (1 - Math.Pow(e.Value, 2)) / (1 + e.Value * Math.Cos(theta.Value))
        );
    }
}
