namespace Afmaths;


public class Position
{
    public Vector3D<double> Vector { get; }

    public Position(Vector3D<double> vector)
    {
        Vector = vector;
    }

    public Position(double x, double y, double z)
    {
        Vector = new Vector3D<double>(x, y, z);
    }

    public Position(Scalar<double> magnitude)
    {
        Vector = new Vector3D<double>(magnitude.Value, 0, 0);
    }

    public Position(double magnitude)
        : this(magnitude, 0, 0)
    {
    }
}