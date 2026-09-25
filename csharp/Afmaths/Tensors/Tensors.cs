namespace Afmaths;

public class Scalar(double value) : PhysicalValue(value)
{
}
public abstract class Vector
{
    public static Vector3D VectorMultiplication(Vector3D a, double scalar)
    {
        return new Vector3D(
            a.X * scalar,
            a.Y * scalar,
            a.Z * scalar
        );
    }

    public static Vector3D VectorAddition(Vector3D a, Vector3D b)
    {
        return new Vector3D(
            a.X + b.X,
            a.Y + b.Y,
            a.Z + b.Z
        );
    }

    public static Vector3D VectorSubtraction(Vector3D a, Vector3D b)
    {
        return new Vector3D(
            a.X - b.X,
            a.Y - b.Y,
            a.Z - b.Z
        );
    }

    public static Vector3D VectorCrossProduct(Vector3D a, Vector3D b)
    {
        return new Vector3D(
            a.Y * b.Z - a.Z * b.Y,
            a.Z * b.X - a.X * b.Z,
            a.X * b.Y - a.Y * b.X
        );
    }
}

public class Vector1D(double x) : Vector
{
    public double X { get; } = x;
}

public class Vector2D(double x, double y) : Vector
{
    public double X { get; } = x;
    public double Y { get; } = y;
}

public class Vector3D(double x, double y, double z) : Vector
{
    public double X { get; } = x;
    public double Y { get; } = y;
    public double Z { get; } = z;


}