namespace Afmaths;

public class Velocity
{
    public Vector3D<double> Vector { get; }

    public Velocity(Vector3D<double> vector)
    {
        Vector = vector;
    }

    public Velocity(double x, double y, double z)
    {
        Vector = new Vector3D<double>(x, y, z);
    }

    public Velocity(Scalar<double> magnitude)
    {
        Vector = new Vector3D<double>(
            magnitude.Value,
            default!,
            default!
        );
    }

    public Velocity(double magnitude)
        : this(magnitude, default!, default!)
    {
    }
}


public class Acceleration(double value) : PhysicalValue(value)
{
}

public class Distance(double value) : PhysicalValue(value)
{
}
