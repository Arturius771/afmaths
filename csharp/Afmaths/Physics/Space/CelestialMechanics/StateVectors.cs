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
        return new Position(
            elements.PerifocalRadialUnitVector().VectorMultiplication(
                celestialMechanics.OrbitEquation(
                    elements.SemiMajorAxis,
                    elements.Eccentricity,
                    elements.TrueAnomaly
                ).Value
            )
        );
    }

    public Velocity PerifocalVelocityCircular(
        OrbitalElements elements,
        GravitationalParameter gravitationalParameter
    )
    {
        return new Velocity(
            elements.PerifocalVelocityDirection().VectorMultiplication(
                Math.Sqrt(
                    gravitationalParameter.Value
                    / elements.SemiMajorAxis.Value
                    * (1 - Math.Pow(elements.Eccentricity.Value, 2))
                )
            )
        );
    }

    public Velocity PerifocalVelocityEllipse(
        OrbitalElements elements,
        GravitationalParameter gravitationalParameter
    )
    {
        double e = elements.Eccentricity.Value;
        double theta = elements.TrueAnomaly.Value;
        double a = elements.SemiMajorAxis.Value;

        double p = a * (1 - e * e);

        double scale = Math.Sqrt(
            gravitationalParameter.Value / p
        );

        return new Velocity(
            -scale * Math.Sin(theta),
            scale * (e + Math.Cos(theta)),
            0
        );
    }

    public OrbitalStateVector FromOrbitalElements(
        OrbitalElements elements,
        GravitationalParameter mu
    )
    {
        var transformation =
            new SpaceTransformations().IntertialReferenceFrameFromPerifocal(elements);

        var position = transformation.OrthonormalFrameTransform(
            PerifocalPosition(elements)
        );

        var velocity = transformation.OrthonormalFrameTransform(
            PerifocalVelocityEllipse(elements, mu)
        );

        return new OrbitalStateVector(
            new Position(
                position.X,
                position.Y,
                position.Z
            ),
            new Velocity(
                velocity.X,
                velocity.Y,
                velocity.Z
            )
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
                    celestialMechanics.KeplerEquation(
                        elements.TrueAnomaly.ToEccentricAnomaly(
                            elements.Eccentricity
                        ),
                        elements.Eccentricity
                    ),
                    timeOffset,
                    elements.SemiMajorAxis.ToMeanMotion(mu)
                )
            ),
            mu
        );
    }

    public RightAscensionAscendingNode ToRightAscensionAscendingNode(
        GravitationalParameter mu
    )
    {
        AngularMomentum h = SpecificAngularMomentum(mu);

        Vector3D<double> n =
            Vector3D<double>.UnitVector().VectorCrossProduct(h);

        double nMagnitude = n.VectorMagnitude();

        if (n.Y >= 0)
        {
            return new RightAscensionAscendingNode(
                Math.Acos(n.X / nMagnitude)
            );
        }

        return new RightAscensionAscendingNode(
            2 * Math.PI - Math.Acos(n.X / nMagnitude)
        );
    }

    public Inclination ToInclination(
        GravitationalParameter mu
    )
    {
        AngularMomentum h = SpecificAngularMomentum(mu);

        return new Inclination(
            Math.Atan2(
                Math.Sqrt(
                    h.X * h.X
                    + h.Y * h.Y
                ),
                h.Z
            )
        );
    }

    public AngularMomentum SpecificAngularMomentum(
        GravitationalParameter mu
    )
    {
        return new AngularMomentum(
            Position.VectorCrossProduct(
                Velocity
            )
        );
    }

    public SemiLatusRectum ToSemiLatusRectum(
        GravitationalParameter mu
    )
    {
        double h = SpecificAngularMomentum(mu)
            .VectorMagnitude();

        return new SemiLatusRectum(
            Math.Pow(h, 2) / mu.Value
        );
    }

    public SemiMajorAxis ToSemiMajorAxis(
        GravitationalParameter mu
    )
    {
        double r = Position.VectorMagnitude();
        double v = Velocity.VectorMagnitude();

        return new SemiMajorAxis(
            Math.Pow(
                (2 / r)
                - (Math.Pow(v, 2) / mu.Value),
                -1
            )
        );
    }

    public Eccentricity ToEccentricity(
        GravitationalParameter mu
    )
    {
        SemiMajorAxis a = ToSemiMajorAxis(mu);

        return new Eccentricity(
            Math.Sqrt(
                1
                - Math.Pow(
                    ToSemiLatusRectum(mu)
                        .ToSemiMinorAxis(a)
                        .Value,
                    2
                )
                / Math.Pow(a.Value, 2)
            )
        );
    }

    public EccentricAnomaly ToEccentricAnomaly(
        GravitationalParameter mu
    )
    {
        SemiMajorAxis a = ToSemiMajorAxis(mu);

        double r = Position.VectorMagnitude();
        double n = a.ToMeanMotion(mu).Value;

        double y =
            Position.VectorDotProduct(Velocity)
            / (n * Math.Pow(a.Value, 2));

        double x =
            1 - r / a.Value;

        return new EccentricAnomaly(
            Math.Atan2(y, x)
        ).NormalizeRadians<EccentricAnomaly>();
    }

    public TrueAnomaly ToTrueAnomaly(
        GravitationalParameter mu
    )
    {
        EccentricAnomaly eccentric =
            ToEccentricAnomaly(mu);

        Eccentricity e =
            ToEccentricity(mu);

        double y =
            Math.Sqrt(
                1 - Math.Pow(e.Value, 2)
            )
            * Math.Sin(eccentric.Value);

        double x =
            Math.Cos(eccentric.Value)
            - e.Value;

        return new TrueAnomaly(
            Math.Atan2(y, x)
        ).NormalizeRadians<TrueAnomaly>();
    }

    public ArgumentOfPeriapsis ToArgumentOfPeriapsis(
        GravitationalParameter mu
    )
    {
        return new ArgumentOfPeriapsis(
            ArgumentOfLatitude(mu).Value
            - ToTrueAnomaly(mu).Value
        ).NormalizeRadians<ArgumentOfPeriapsis>();
    }

    public Latitude ArgumentOfLatitude(
        GravitationalParameter mu
    )
    {
        Inclination i =
            ToInclination(mu);

        RightAscensionAscendingNode raan =
            ToRightAscensionAscendingNode(mu);

        double y =
            Position.Z
            / Math.Sin(i.Value);

        double x =
            Position.X * Math.Cos(raan.Value)
            + Position.Y * Math.Sin(raan.Value);

        return new Latitude(
            Math.Atan2(y, x)
        ).NormalizeRadians<Latitude>();
    }

    public OrbitalElements ToOrbitalElements(
        GravitationalParameter mu
    )
    {
        return new OrbitalElements(
            ToSemiMajorAxis(mu),
            ToEccentricity(mu),
            ToInclination(mu),
            ToRightAscensionAscendingNode(mu),
            ToArgumentOfPeriapsis(mu),
            ToTrueAnomaly(mu)
        );
    }
}