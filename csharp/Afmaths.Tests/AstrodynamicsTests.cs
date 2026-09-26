using Xunit;

namespace Afmaths.Tests;

public class AstrodynamicsTests
{
    [Fact]
    public void PhaseOrbit_WithCurrentTrueAnomaly_ReturnsEquivalentOrbit()
    {
        var mu = GravitationalParameter.EarthGravitationalParameter;

        var elements = new OrbitalElements(
            new SemiMajorAxis(384_448_000),
            new Eccentricity(0.590095),
            new Inclination(0.0),
            new RightAscensionAscendingNode(0.0),
            new ArgumentOfPeriapsis(0.0),
            new TrueAnomaly(0.0)
        );

        var manoeuvre = new Manoeuvre(new Orbit(elements, mu));

        var result = manoeuvre.PhaseOrbit(
            elements.TrueAnomaly,
            mu
        );

        Assert.Equal(
            384_447_999.9999996,
            result.Elements.SemiMajorAxis.Value,
            7
        );

        Assert.Equal(
            elements.Eccentricity.Value,
            result.Elements.Eccentricity.Value,
            7
        );

        Assert.Equal(
            elements.Inclination.Value,
            result.Elements.Inclination.Value,
            7
        );

        Assert.Equal(
            elements.RightAscensionOfAscendingNode.Value,
            result.Elements.RightAscensionOfAscendingNode.Value,
            7
        );

        Assert.Equal(
            elements.ArgumentOfPeriapsis.Value,
            result.Elements.ArgumentOfPeriapsis.Value,
            7
        );

        Assert.Equal(
            elements.TrueAnomaly.Value,
            result.Elements.TrueAnomaly.Value,
            7
        );
    }

    [Fact]
    public void PhaseOrbit_WithDifferentTarget_ReturnsExpectedPhaseOrbit()
    {
        var mu = GravitationalParameter.EarthGravitationalParameter;

        var elements = new OrbitalElements(
            new SemiMajorAxis(384_448_000),
            new Eccentricity(0.590095),
            new Inclination(0.0),
            new RightAscensionAscendingNode(0.0),
            new ArgumentOfPeriapsis(0.0),
            new TrueAnomaly(0.0)
        );

        var manoeuvre = new Manoeuvre(new Orbit(elements, mu));

        var target = new TrueAnomaly(5.0);

        var result = manoeuvre.PhaseOrbit(
            target,
            mu
        );

        Assert.Equal(
            397_942_694.76110512,
            result.Elements.SemiMajorAxis.Value,
            7
        );

        Assert.Equal(
            0.590095,
            result.Elements.Eccentricity.Value,
            5
        );

        Assert.Equal(
            elements.Inclination.Value,
            result.Elements.Inclination.Value,
            7
        );

        Assert.Equal(
            elements.RightAscensionOfAscendingNode.Value,
            result.Elements.RightAscensionOfAscendingNode.Value,
            7
        );

        Assert.Equal(
            elements.ArgumentOfPeriapsis.Value,
            result.Elements.ArgumentOfPeriapsis.Value,
            7
        );

        Assert.Equal(
            elements.TrueAnomaly.Value,
            result.Elements.TrueAnomaly.Value,
            7
        );
    }
}