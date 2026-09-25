namespace Afmaths;

public class OrbitalStateVector : StateVector
{
    private static readonly CelestialMechanics celestialMechanics = new();

    public OrbitalStateVector(Position position, Velocity velocity)
        : base(position, velocity)
    {
    }

    public Position PerifocalPosition(OrbitalElements elements)
    {

        return new Position(Vector3D<double>.VectorMultiplication(
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


        return new Velocity(Vector3D<double>.VectorMultiplication(
            elements.PerifocalVelocityDirection(),
            Math.Sqrt(
            gravitationalParameter.Value
            / elements.SemiMajorAxis.Value
            * (1 - Math.Pow(elements.Eccentricity.Value, 2))
        )
        ));
    }

    public OrbitalStateVector FromOrbitalElements(
    OrbitalElements elements,
    GravitationalParameter mu
)
    {
        var transformation =
            new SpaceTransformations().IntertialReferenceFrameFromPerifocal(elements);

        var position = transformation.OrthonormalFrameTransform(
            PerifocalPosition(elements).Vector
        );

        var velocity = transformation.OrthonormalFrameTransform(
            PerifocalVelocity(elements, mu).Vector
        );


        return new OrbitalStateVector(
            new Position(position.X, position.Y, position.Z),
            new Velocity(velocity.X, velocity.Y, velocity.Z)
        );
    }

    public OrbitalStateVector FromOrbitalElementsWithTimeOffset(
        OrbitalElements elements,
        GravitationalParameter mu,
        Time timeOffset
    )
    {
        return FromOrbitalElements(
            new OrbitalElements(
                elements.SemiMajorAxis,
                elements.Eccentricity,
                elements.Inclination,
                elements.RightAscensionOfAscendingNode,
                elements.ArgumentOfPeriapsis,
                elements.TrueAnomaly.AtTime(
                    elements.Eccentricity,
                    celestialMechanics.KeplerEquation(elements.TrueAnomaly.ToEccentricAnomaly(elements.Eccentricity), elements.Eccentricity),
                    timeOffset,
                    elements.SemiMajorAxis.MeanMotion(mu)
                )
            ),
            mu
        );
    }
}