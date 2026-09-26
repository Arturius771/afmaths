namespace Afmaths;

/// <summary>
/// Represents a velocity vector in three-dimensional space.
/// </summary>
public class Velocity : Vector3D<double>
{
    public Velocity(double x, double y, double z)
        : base(x, y, z)
    {
    }

    /// <summary>
    /// Initializes a new instance of the <see cref="Velocity"/> class with the specified magnitude along the x-axis.
    /// </summary>
    /// <param name="magnitude">The magnitude of the velocity vector.</param>
    public Velocity(double magnitude)
        : this(magnitude, 0, 0)
    {
    }

    public Velocity(Vector3D<double> vector)
        : base(vector.X, vector.Y, vector.Z)
    {
    }
}


public class Acceleration(double value) : PhysicalValue<Acceleration>(value)
{
    protected override Acceleration Create(double value) => new(value);
}

