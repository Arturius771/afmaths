namespace Afmaths;

public class SpaceTransformations
{
    /// <summary>
    /// Transforms from the perifocal reference frame to the inertial reference frame.
    /// </summary>
    /// <param name="elements">The orbital elements defining the orbit.</param>
    /// <returns>The transformation matrix from the perifocal frame to the inertial frame.</returns>
    public TransformationMatrix IntertialReferenceFrameFromPerifocal(OrbitalElements elements)
    {
        double aop = elements.ArgumentOfPeriapsis.Value;
        double raan = elements.RightAscensionOfAscendingNode.Value;
        double i = elements.Inclination.Value;

        double[] p = [Math.Cos(aop) * Math.Cos(raan) - Math.Sin(aop) * Math.Cos(i) * Math.Sin(raan), Math.Cos(aop) * Math.Sin(raan) + Math.Sin(aop) * Math.Cos(i) * Math.Cos(raan), Math.Sin(aop) * Math.Sin(i)];
        double[] q = [-Math.Sin(aop) * Math.Cos(raan) - Math.Cos(aop) * Math.Cos(i) * Math.Sin(raan), -Math.Sin(aop) * Math.Sin(raan) + Math.Cos(aop) * Math.Cos(i) * Math.Cos(raan), Math.Cos(aop) * Math.Sin(i)];
        double[] w = [Math.Sin(i) * Math.Sin(raan), -Math.Sin(i) * Math.Cos(raan), Math.Cos(i)];


        return new TransformationMatrix(
            new Vector3D<double>(p[0], q[0], w[0]),
            new Vector3D<double>(p[1], q[1], w[1]),
            new Vector3D<double>(p[2], q[2], w[2])
        );
    }
}