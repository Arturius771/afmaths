using System.Numerics;

namespace Afmaths;

public class Scalar<T>(T value) : PhysicalValue<Scalar<T>>(Convert.ToDouble(value))
{
    protected override Scalar<T> Create(double value) => new((T)Convert.ChangeType(value, typeof(T)));
}


public abstract class Vector<T>
    where T : INumber<T>
{
    public abstract double VectorMagnitude();
}

public class Vector1D<T>(T x) : Vector<T>
    where T : INumber<T>
{
    public T X { get; } = x;

    public override double VectorMagnitude()
    {
        return Math.Sqrt(Convert.ToDouble(X * X));
    }
}

public class Vector2D<T>(T x, T y) : Vector<T>
    where T : INumber<T>
{
    public T X { get; } = x;
    public T Y { get; } = y;

    public override double VectorMagnitude()
    {
        return Math.Sqrt(Convert.ToDouble(X * X + Y * Y));
    }
}

public class Vector3D<T>(T x, T y, T z) : Vector<T>
    where T : INumber<T>
{
    public T X { get; } = x;
    public T Y { get; } = y;
    public T Z { get; } = z;

    public static Vector3D<T> Zero => new Vector3D<T>(T.Zero, T.Zero, T.Zero);
    public Vector3D<double> AsDouble => new Vector3D<double>(
        Convert.ToDouble(X),
        Convert.ToDouble(Y),
        Convert.ToDouble(Z)
    );

    public Vector3D<T> VectorMultiplication(
        T scalar
    )
    {
        return new Vector3D<T>(
            X * scalar,
            Y * scalar,
            Z * scalar
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

    public Vector3D<T> VectorCrossProduct(
        Vector3D<T> b
    )
    {
        return new Vector3D<T>(
            Y * b.Z - Z * b.Y,
            Z * b.X - X * b.Z,
            X * b.Y - Y * b.X
        );
    }

    public T VectorDotProduct(
        Vector3D<T> b
    )
    {
        return X * b.X
            + Y * b.Y
            + Z * b.Z;
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

    public Vector3D<T> VectorNormalise()
    {
        var magnitude = this.VectorMagnitude();

        return new Vector3D<T>(
            (T)Convert.ChangeType(Convert.ToDouble(this.X) / magnitude, typeof(T)),
            (T)Convert.ChangeType(Convert.ToDouble(this.Y) / magnitude, typeof(T)),
            (T)Convert.ChangeType(Convert.ToDouble(this.Z) / magnitude, typeof(T))
        );
    }

    public override double VectorMagnitude()
    {
        return Math.Sqrt(
                Convert.ToDouble(X * X + Y * Y + Z * Z)
            );
    }

    public static Vector3D<T> UnitVector()
    {
        return new Vector3D<T>(T.Zero, T.Zero, T.One);
    }
}