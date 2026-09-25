namespace Afmaths;

public class StateVector
{
    public Position Position { get; }
    public Velocity Velocity { get; }

    private static readonly CelestialMechanics celestialMechanics = new();

    public StateVector(Position position, Velocity velocity)
    {
        Position = position;
        Velocity = velocity;
    }

    public Position PerifocalPosition(OrbitalElements elements)
    {

        return new Position(Vector.VectorMultiplication(
            elements.PerifocalRadialUnitVector(),
            celestialMechanics.OrbitEquation(
            elements.SemiMajorAxis,
            elements.Eccentricity,
            elements.TrueAnomaly
        ).Value));
    }

    public Velocity PerifocalVelocity(
        OrbitalElements elements,
        GravitationalParameter gravitationalParameter
    )
    {


        return new Velocity(Vector.VectorMultiplication(
            elements.PerifocalVelocityDirection(),
            Math.Sqrt(
            gravitationalParameter.Value
            / elements.SemiMajorAxis.Value
            * (1 - Math.Pow(elements.Eccentricity.Value, 2))
        )
        ));
    }

    public StateVector FromOrbitalElements(
        OrbitalElements elements,
        GravitationalParameter mu
    )
    {
        return new StateVector(
            PerifocalPosition(elements),
            PerifocalVelocity(elements, mu)
        );
    }
}