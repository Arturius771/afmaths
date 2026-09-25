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

        Assert.Equal(expected, ((Vector3D<double>)result.Vector).X, 6);
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
        var trueAnomaly = new TrueAnomaly(0.2);

        var elements = new OrbitalElements(
            semiMajorAxis,
            eccentricity,
            inclination,
            raan,
            argumentOfPeriapsis,
            trueAnomaly
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
        Assert.Same(trueAnomaly, elements.TrueAnomaly);
    }

    [Fact]
    public void EarthGravitationalParameter_HasExpectedValue()
    {
        Assert.Equal(
            3.98589196e14,
            GravitationalParameter.EarthGravitationalParameter.Value
        );
    }

    [Fact]
    public void OrbitalStateVector_WithTimeOffset_ReturnsExpectedStateVector()
    {
        var elements = new OrbitalElements(
            new SemiMajorAxis(6_878_100),
            new Eccentricity(10e-5),
            new Inclination(98.371 * Math.PI / 180.0),
            new RightAscensionAscendingNode(120.534 * Math.PI / 180.0),
            new ArgumentOfPeriapsis(10.598 * Math.PI / 180.0),
            new TrueAnomaly(2.8022276030554347)
        );

        var initialStateVector = new OrbitalStateVector(
            new Position(0, 0, 0),
            new Velocity(new Vector3D<double>(0, 0, 0))
        );

        var result = initialStateVector.FromOrbitalElementsWithTimeOffset(
            elements,
            GravitationalParameter.EarthGravitationalParameter,
            // new GravitationalParameter(3.986004418e14),
            new Time(1800)
        );

        Assert.Equal(
            -1_753_046.9002415095,
            result.Position.Vector.X,
            2
        );
        Assert.Equal(
            1_070_837.1082100407,
            result.Position.Vector.Y,
            2
        );
        Assert.Equal(
            -6_564_116.1096390644,
            result.Position.Vector.Z,
            2
        );

        var velocity = Assert.IsType<Vector3D<double>>(result.Velocity.Vector);

        Assert.Equal(
            -3_479.1501727911755,
            velocity.X,
            2
        );
        Assert.Equal(
            6_473.405491247755,
            velocity.Y,
            2
        );
        Assert.Equal(
            1_985.1989246914095,
            velocity.Z,
            2
        );
    }
}