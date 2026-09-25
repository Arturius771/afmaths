namespace Afmaths;

public class Velocity
{
    public Vector Vector { get; }

    public Velocity(Vector vector)
    {
        Vector = vector;
    }

    public Velocity(Scalar magnitude)
    {
        Vector = new Vector1D(magnitude.Value);
    }

    public Velocity(double magnitude)
        : this(new Scalar(magnitude))
    {
    }
}


public class Acceleration(double value) : PhysicalValue(value)
{
}

public class Distance(double value) : PhysicalValue(value)
{
}
