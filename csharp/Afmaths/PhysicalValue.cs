namespace Afmaths;

public class PhysicalValue
{
    public double Value { get; }

    public PhysicalValue(double value)
    {
        Value = value;
    }
}

public class Velocity(double value) : PhysicalValue(value)
{
}

public class Acceleration(double value) : PhysicalValue(value)
{
}

public class Distance(double value) : PhysicalValue(value)
{
}

public class Mass(double value) : PhysicalValue(value)
{
}