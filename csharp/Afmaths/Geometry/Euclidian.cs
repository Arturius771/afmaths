namespace Afmaths;

public class EuclidianDistance
{
    public Distance Between(Vector3D<double> a, Vector3D<double> b)
    {
        var difference = new Vector3D<double>(
            a.X - b.X,
            a.Y - b.Y,
            a.Z - b.Z
        );
        return new Distance(Math.Sqrt(
            Math.Pow(difference.X, 2) +
            Math.Pow(difference.Y, 2) +
            Math.Pow(difference.Z, 2)
        ));
    }

    public Distance GeometricMeanDistance(Distance a, Distance b)
    {
        return new Distance(Math.Sqrt(a.Value * b.Value));
    }
}