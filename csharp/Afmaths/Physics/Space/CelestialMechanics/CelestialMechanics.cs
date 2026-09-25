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
            a.Value * (1 - Math.Pow(e.Value, 2)) / (1 + e.Value * Math.Cos(theta.Value))
        );
    }

    public Rate MeanAngularRate(SemiMajorAxis a, GravitationalParameter mu)
    {
        // n = sqrt(mu / a^3)
        return new Rate(
            Math.Sqrt(mu.Value / Math.Pow(a.Value, 3))
        );
    }
}
