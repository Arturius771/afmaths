namespace Afmaths;


public class Position : Vector3D<double>
{
    EuclidianDistance euclidianDistance = new();

    public Position(double x, double y, double z)
        : base(x, y, z)
    {
    }

    public Position(double magnitude)
        : this(magnitude, 0, 0)
    {

    }

    public Position(Vector3D<double> vector)
        : base(vector.X, vector.Y, vector.Z)
    {
    }

    public Distance DistanceFrom(Position other)
    {
        return euclidianDistance.Between(this.AsDouble, other.AsDouble);
    }
}

public class Distance(double value) : PhysicalValue(value)
{

}
