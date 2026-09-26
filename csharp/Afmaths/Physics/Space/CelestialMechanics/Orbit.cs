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

    public Orbit(
        OrbitalElements orbitalElements,
        GravitationalParameter mu
    )
    {
        Elements = orbitalElements;

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
    }
}