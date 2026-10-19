namespace Afmaths;

/// <summary>
/// Represents an orbit in space, defined by its orbital elements and state vector.
/// </summary>
public class Orbit
{
    /// <summary>
    /// Gets the orbital elements defining this orbit.
    /// </summary>
    public OrbitalElements Elements { get; }
    /// <summary>
    /// Gets the state vector of this orbit.
    /// </summary>
    public OrbitalStateVector StateVector { get; }

    public GravitationalParameter Mu { get; }

    /// <summary>
    /// Initializes a new instance of the <see cref="Orbit"/> class using the specified orbital elements and gravitational parameter.
    /// </summary>
    /// <param name="orbitalElements">The orbital elements defining the orbit.</param>
    /// <param name="mu">The gravitational parameter of the central body.</param>
    public Orbit(
        OrbitalElements orbitalElements,
        GravitationalParameter mu
    )
    {
        Elements = orbitalElements;
        Mu = mu;

        StateVector =
            new OrbitalStateVector()
                .FromOrbitalElements(
                    orbitalElements,
                    mu
                );
    }

    public Orbit(
        OrbitalStateVector orbitalStateVector,
        GravitationalParameter mu
    )
    {
        StateVector = orbitalStateVector;
        Elements = orbitalStateVector.ToOrbitalElements(mu);
        Mu = mu;
    }

    public Distance OrbitalRadius => new Kepler().OrbitEquation(Elements.SemiMajorAxis, Elements.Eccentricity, Elements.TrueAnomaly);
}