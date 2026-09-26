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
            GravitationalParameter.EarthGravitationalParameter.Value
            / radius.Value
        );

        Assert.Equal(
            expected,
            ((Vector3D<double>)result).X,
            6
        );
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

        Assert.Same(
            semiMajorAxis,
            elements.SemiMajorAxis
        );

        Assert.Same(
            eccentricity,
            elements.Eccentricity
        );

        Assert.Same(
            inclination,
            elements.Inclination
        );

        Assert.Same(
            raan,
            elements.RightAscensionOfAscendingNode
        );

        Assert.Same(
            argumentOfPeriapsis,
            elements.ArgumentOfPeriapsis
        );

        Assert.Same(
            trueAnomaly,
            elements.TrueAnomaly
        );
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
            new Inclination(
                98.371 * Math.PI / 180.0
            ),
            new RightAscensionAscendingNode(
                120.534 * Math.PI / 180.0
            ),
            new ArgumentOfPeriapsis(
                10.598 * Math.PI / 180.0
            ),
            new TrueAnomaly(
                2.8022276030554347
            )
        );

        var initialStateVector = new OrbitalStateVector(
            new Position(0, 0, 0),
            new Velocity(0, 0, 0)
        );

        var result =
            initialStateVector.FromOrbitalElementsWithTimeOffset(
                elements,
                GravitationalParameter.EarthGravitationalParameter,
                new Time(1800)
            );

        Assert.Equal(
            -1_753_046.9002415095,
            result.Position.X,
            2
        );

        Assert.Equal(
            1_070_837.1082100407,
            result.Position.Y,
            2
        );

        Assert.Equal(
            -6_564_116.1096390644,
            result.Position.Z,
            2
        );

        Assert.Equal(
            -3_478.9852487725434,
            result.Velocity.X,
            2
        );

        Assert.Equal(
            6_473.34030790454,
            result.Velocity.Y,
            2
        );

        Assert.Equal(
            1_985.9392391364208,
            result.Velocity.Z,
            2
        );
    }

    [Fact]
    public void OrbitalStateVector_WithNoTimeOffset_ReturnsExpectedStateVector()
    {
        var elements = new OrbitalElements(
            new SemiMajorAxis(6_878_100),
            new Eccentricity(10e-5),
            new Inclination(
                98.371 * Math.PI / 180.0
            ),
            new RightAscensionAscendingNode(
                120.534 * Math.PI / 180.0
            ),
            new ArgumentOfPeriapsis(
                10.598 * Math.PI / 180.0
            ),
            new TrueAnomaly(
                2.8022276030554347
            )
        );

        var initialStateVector = new OrbitalStateVector(
            new Position(0, 0, 0),
            new Velocity(0, 0, 0)
        );

        var result =
            initialStateVector.FromOrbitalElements(
                elements,
                GravitationalParameter.EarthGravitationalParameter
            );

        Assert.Equal(
            3_585_820.0493523744,
            result.Position.X,
            2
        );

        Assert.Equal(
            -5_776_139.5360282371,
            result.Position.Y,
            2
        );

        Assert.Equal(
            1_046_560.3556216198,
            result.Position.Z,
            2
        );

        Assert.Equal(
            -348.2861279964011,
            result.Velocity.X,
            2
        );

        Assert.Equal(
            -1_564.744830104527,
            result.Velocity.Y,
            2
        );

        Assert.Equal(
            -7_441.090135767868,
            result.Velocity.Z,
            2
        );
    }

    [Fact]
    public void StateVector_WithNoTimeOffset_ReturnsExpectedOrbitalElements()
    {
        var expected = new OrbitalElements(
            new SemiMajorAxis(6_878_100),
            new Eccentricity(10e-5),
            new Inclination(
                98.371 * Math.PI / 180.0
            ),
            new RightAscensionAscendingNode(
                120.534 * Math.PI / 180.0
            ),
            new ArgumentOfPeriapsis(
                10.598 * Math.PI / 180.0
            ),
            new TrueAnomaly(
                2.8022276030554347
            )
        );

        var initialStateVector = new OrbitalStateVector(
            new Position(0, 0, 0),
            new Velocity(0, 0, 0)
        );

        var stateVector =
            initialStateVector.FromOrbitalElements(
                expected,
                GravitationalParameter.EarthGravitationalParameter
            );

        var result =
            stateVector.ToOrbitalElements(
                GravitationalParameter.EarthGravitationalParameter
            );

        Assert.Equal(
            expected.SemiMajorAxis.Value,
            result.SemiMajorAxis.Value,
            2
        );

        Assert.Equal(
            expected.Eccentricity.Value,
            result.Eccentricity.Value,
            6
        );

        Assert.Equal(
            expected.Inclination.Value,
            result.Inclination.Value,
            6
        );

        Assert.Equal(
            expected.RightAscensionOfAscendingNode.Value,
            result.RightAscensionOfAscendingNode.Value,
            6
        );

        Assert.Equal(
            expected.ArgumentOfPeriapsis.Value,
            result.ArgumentOfPeriapsis.Value,
            6
        );

        Assert.Equal(
            expected.TrueAnomaly.Value,
            result.TrueAnomaly.Value,
            6
        );
    }
}