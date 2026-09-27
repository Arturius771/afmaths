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

public class Coordinate2D : Vector2D<double>
{
    public Coordinate2D(double x, double y) : base(x, y) { }
}

public class Coordinate3D : Vector3D<double>
{
    public Coordinate3D(double x, double y, double z) : base(x, y, z) { }
}

public class CoordinateSystem<T, U, V>
{
    public T Latitude { get; }
    public U Longitude { get; }
    public V? Altitude { get; }
    public CoordinateSystem(Coordinate2D position)
    {
        Latitude = (T)Activator.CreateInstance(typeof(T), position.X)!;
        Longitude = (U)Activator.CreateInstance(typeof(U), position.Y)!;
        Altitude = default(V);
    }

    public CoordinateSystem(Coordinate3D position)
    {
        Latitude = (T)Activator.CreateInstance(typeof(T), position.X)!;
        Longitude = (U)Activator.CreateInstance(typeof(U), position.Y)!;
        Altitude = (V)Activator.CreateInstance(typeof(V), position.Z)!;
    }
}

public class Orientation(Vector3D<double> value)
{
    public Vector3D<double> Value { get; } = value;
}

public class ReferenceSystem<T, U, V>(CoordinateSystem<T, U, V> coordinateSystem, Vector3D<double> orientation)
{
    public CoordinateSystem<T, U, V> CoordinateSystem { get; } = coordinateSystem;
    public Vector3D<double> Orientation { get; } = orientation;
}

public class Geographic : CoordinateSystem<Latitude, Longitude, object>
{
    public Geographic(Latitude latitude, Longitude longitude)
        : base(new Coordinate2D(latitude.Value, longitude.Value))
    {
    }
}

public class Cartesian : CoordinateSystem<Longitude, Latitude, Altitude>
{
    public Cartesian(double x, double y, double z)
        : base(new Coordinate3D(x, y, z))
    {
    }

    public Cartesian(double x, double y)
        : base(new Coordinate2D(x, y))
    {
    }
}

public class Polar : CoordinateSystem<Longitude, Latitude, Altitude>
{
    public Polar(double radius, double azimuth, double elevation)
        : base(new Coordinate3D(radius, azimuth, elevation))
    {
    }
}

public class Equatorial : CoordinateSystem<RightAscension, Declination, object>
{
    public Equatorial(RightAscension rightAscension, Declination declination)
        : base(new Coordinate2D(rightAscension.Value, declination.Value))
    {
    }

    public Equatorial(HourAngle hourAngle, Declination declination)
        : base(new Coordinate2D(hourAngle.Value, declination.Value))
    {
    }
}

public class Azimuth(double value) : Longitude(value)
{
    protected override Azimuth Create(double value) => new(value);
}

public class Horizontal : CoordinateSystem<Azimuth, Altitude, object>
{
    public Horizontal(Azimuth azimuth, Altitude elevation)
        : base(new Coordinate2D(azimuth.Value, elevation.Value))
    {
    }
}

public class Ecliptic : CoordinateSystem<Longitude, Latitude, object>
{
    public Ecliptic(Longitude longitude, Latitude latitude)
        : base(new Coordinate2D(longitude.Value, latitude.Value))
    {
    }
}

public class Galactic : CoordinateSystem<Longitude, Latitude, object>
{
    public Galactic(Longitude longitude, Latitude latitude)
        : base(new Coordinate2D(longitude.Value, latitude.Value))
    {
    }
}