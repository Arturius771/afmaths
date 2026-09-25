namespace Afmaths;

public class TransformationMatrix
{
    private readonly Vector3D<double> _row1;
    private readonly Vector3D<double> _row2;
    private readonly Vector3D<double> _row3;

    public TransformationMatrix(
        Vector3D<double> row1,
        Vector3D<double> row2,
        Vector3D<double> row3
    )
    {
        _row1 = row1;
        _row2 = row2;
        _row3 = row3;
    }

    public Vector3D<double> OrthonormalFrameTransform(
        Vector3D<double> vector
    )
    {
        return new Vector3D<double>(
            Vector3D<double>.VectorDotProduct(_row1, vector),
            Vector3D<double>.VectorDotProduct(_row2, vector),
            Vector3D<double>.VectorDotProduct(_row3, vector)
        );
    }
}