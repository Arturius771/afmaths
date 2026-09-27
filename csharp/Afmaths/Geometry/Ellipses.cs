namespace Afmaths;

public class Angle
{
    public double Value { get; }

    public Angle(double value)
    {
        Value = value;
    }
}
public class Radians : Angle
{
    public Radians(double value) : base(value) { }
}

public class Ellipse
{
    public double SemiMajorAxis { get; }
    public double SemiMinorAxis { get; }

    public Ellipse(double semiMajorAxis, double semiMinorAxis)
    {
        SemiMajorAxis = semiMajorAxis;
        SemiMinorAxis = semiMinorAxis;
    }

    public List<Radians> GenerateAngles(int resolution)
    {
        return new Operations().Interval<Radians>(0, 2 * Math.PI, resolution);
    }
}