namespace Afmaths;

public class Latitude(double value) : PhysicalValue<Latitude>(value)
{
    protected override Latitude Create(double value) => new(value);
}

public class Longitude(double value) : PhysicalValue<Longitude>(value)
{
    protected override Longitude Create(double value) => new(value);
}

public class Altitude(double value) : PhysicalValue<Altitude>(value)
{
    protected override Altitude Create(double value) => new(value);
}

public class RightAscension(double value) : Longitude(value)
{
    protected override RightAscension Create(double value) => new(value);
}

public class Declination(double value) : Latitude(value)
{
    protected override Declination Create(double value) => new(value);
}

public class HourAngle(double value) : Longitude(value)
{
    protected override HourAngle Create(double value) => new(value);
}

public class CoordinateSystem(Vector3D<double> position)
{
    public Latitude Latitude { get; } = new Latitude(position.X);
    public Longitude Longitude { get; } = new Longitude(position.Y);
    public Altitude Altitude { get; } = new Altitude(position.Z);
}

public class Orientation(Vector3D<double> value)
{
    public Vector3D<double> Value { get; } = value;
}

public class ReferenceSystem(CoordinateSystem coordinateSystem, Vector3D<double> orientation)
{
    public CoordinateSystem CoordinateSystem { get; } = coordinateSystem;
    public Vector3D<double> Orientation { get; } = orientation;
}

public class Geographic : CoordinateSystem
{
    public Geographic(Latitude latitude, Longitude longitude)
        : base(new Vector3D<double>(latitude.Value, longitude.Value, 0))
    {
    }
}

public class Cartesian : CoordinateSystem
{
    public Cartesian(double x, double y, double z)
        : base(new Vector3D<double>(x, y, z))
    {
    }
}

public class Polar : CoordinateSystem
{
    public Polar(double radius, double azimuth, double elevation)
        : base(new Vector3D<double>(radius, azimuth, elevation))
    {
    }
}

public class Equatorial : CoordinateSystem
{
    public Equatorial(RightAscension rightAscension, Declination declination)
        : base(new Vector3D<double>(rightAscension.Value, declination.Value, 0))
    {
    }

    public Equatorial(HourAngle hourAngle, Declination declination)
        : base(new Vector3D<double>(hourAngle.Value, declination.Value, 0))
    {
    }
}

public class Azimuth(double value) : Longitude(value)
{
    protected override Azimuth Create(double value) => new(value);
}

public class Horizontal : CoordinateSystem
{
    public Horizontal(Azimuth azimuth, Altitude elevation)
        : base(new Vector3D<double>(azimuth.Value, elevation.Value, 0))
    {
    }
}

public class Ecliptic : CoordinateSystem
{
    public Ecliptic(Longitude longitude, Latitude latitude)
        : base(new Vector3D<double>(longitude.Value, latitude.Value, 0))
    {
    }
}

public class Galactic : CoordinateSystem
{
    public Galactic(Longitude longitude, Latitude latitude)
        : base(new Vector3D<double>(longitude.Value, latitude.Value, 0))
    {
    }
}