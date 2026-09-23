using Xunit;

namespace Afmaths.Tests;

public class CelestialMechanicsTests
{
    private readonly CelestialMechanics celestialMechanics = new();

    [Fact]
    public void KeplerEquation_ReturnsExpectedMeanAnomaly()
    {
        var eccentricAnomaly = new EccentricAnomaly(1.0);
        var eccentricity = new Eccentricity(0.1);

        var result = celestialMechanics.KeplerEquation(
            eccentricAnomaly,
            eccentricity
        );

        var expected = 1.0 - 0.1 * Math.Sin(1.0);

        Assert.Equal(expected, result.Value, 12);
    }

    [Fact]
    public void VisViva_ReturnsCircularOrbitVelocity()
    {
        var radius = new Distance(7_000_000);
        var semiMajorAxis = new SemiMajorAxis(7_000_000);

        var result = celestialMechanics.VisViva(
            GravitationalParameter.EarthGravitationalParameter,
            radius,
            semiMajorAxis
        );

        var expected = Math.Sqrt(
            GravitationalParameter.EarthGravitationalParameter.Value / radius.Value
        );

        Assert.Equal(expected, result.Value, 6);
    }

    [Fact]
    public void OrbitEquation_AtPeriapsis_ReturnsExpectedRadius()
    {
        var semiMajorAxis = new SemiMajorAxis(10_000);
        var eccentricity = new Eccentricity(0.2);
        var trueAnomaly = new TrueAnomaly(0.0);

        var result = celestialMechanics.OrbitEquation(
            semiMajorAxis,
            eccentricity,
            trueAnomaly
        );

        var expected = 8_000.0;

        Assert.Equal(expected, result.Value, 10);
    }

    [Fact]
    public void OrbitalElements_StoresProvidedValues()
    {
        var semiMajorAxis = new SemiMajorAxis(7_000_000);
        var eccentricity = new Eccentricity(0.01);
        var inclination = new Inclination(0.5);
        var raan = new RightAscensionAscendingNode(1.0);
        var argumentOfPeriapsis = new ArgumentOfPeriapsis(0.3);
        var meanAnomaly = new MeanAnomaly(0.2);

        var elements = new OrbitalElements(
            semiMajorAxis,
            eccentricity,
            inclination,
            raan,
            argumentOfPeriapsis,
            meanAnomaly
        );

        Assert.Same(semiMajorAxis, elements.SemiMajorAxis);
        Assert.Same(eccentricity, elements.Eccentricity);
        Assert.Same(inclination, elements.Inclination);
        Assert.Same(
            raan,
            elements.RightAscensionOfAscendingNode
        );
        Assert.Same(
            argumentOfPeriapsis,
            elements.ArgumentOfPeriapsis
        );
        Assert.Same(meanAnomaly, elements.MeanAnomaly);
    }

    [Fact]
    public void EarthGravitationalParameter_HasExpectedValue()
    {
        Assert.Equal(
            3.986004418e14,
            GravitationalParameter.EarthGravitationalParameter.Value
        );
    }
}