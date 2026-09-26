namespace Afmaths;

public class Velocity : Vector3D<double>
{
    public Velocity(double x, double y, double z)
        : base(x, y, z)
    {
    }

    public Velocity(double magnitude)
        : this(magnitude, 0, 0)
    {
    }

    public Velocity(Vector3D<double> vector)
        : base(vector.X, vector.Y, vector.Z)
    {
    }
}


public class Acceleration(double value) : PhysicalValue(value)
{
}

