using System.Numerics;

namespace Afmaths;

public class Scalar<T>(T value) : PhysicalValue(Convert.ToDouble(value))
{
}

public abstract class Vector<T>
    where T : INumber<T>
{
}

public class Vector1D<T>(T x) : Vector<T>
    where T : INumber<T>
{
    public T X { get; } = x;
}

public class Vector2D<T>(T x, T y) : Vector<T>
    where T : INumber<T>
{
    public T X { get; } = x;
    public T Y { get; } = y;
}

public class Vector3D<T>(T x, T y, T z) : Vector<T>
    where T : INumber<T>
{
    public T X { get; } = x;
    public T Y { get; } = y;
    public T Z { get; } = z;

    public static Vector3D<T> VectorMultiplication(
        Vector3D<T> a,
        T scalar
    )
    {
        return new Vector3D<T>(
            a.X * scalar,
            a.Y * scalar,
            a.Z * scalar
        );
    }

    public static Vector3D<T> VectorAddition(
        Vector3D<T> a,
        Vector3D<T> b
    )
    {
        return new Vector3D<T>(
            a.X + b.X,
            a.Y + b.Y,
            a.Z + b.Z
        );
    }

    public static Vector3D<T> VectorSubtraction(
        Vector3D<T> a,
        Vector3D<T> b
    )
    {
        return new Vector3D<T>(
            a.X - b.X,
            a.Y - b.Y,
            a.Z - b.Z
        );
    }

    public static Vector3D<T> VectorCrossProduct(
        Vector3D<T> a,
        Vector3D<T> b
    )
    {
        return new Vector3D<T>(
            a.Y * b.Z - a.Z * b.Y,
            a.Z * b.X - a.X * b.Z,
            a.X * b.Y - a.Y * b.X
        );
    }

    public static T VectorDotProduct(
        Vector3D<T> a,
        Vector3D<T> b
    )
    {
        return a.X * b.X
            + a.Y * b.Y
            + a.Z * b.Z;
    }

    public static Vector3D<T> VectorTranspose(
        Vector3D<T> a
    )
    {
        return new Vector3D<T>(
            a.X,
            a.Y,
            a.Z
        );
    }
}