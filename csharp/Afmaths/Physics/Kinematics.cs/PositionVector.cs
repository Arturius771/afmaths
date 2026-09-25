namespace Afmaths;


public class Position(double x, double y, double z) : Vector3D(x, y, z)
{
    public Position(Vector3D vector) : this(vector.X, vector.Y, vector.Z)
    {
    }
}