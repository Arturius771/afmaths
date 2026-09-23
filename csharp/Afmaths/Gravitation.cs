namespace Afmaths;

public class GravitationalConstant
{
    public double Value { get; }

    public GravitationalConstant()
    {
        Value = 6.67430e-11;
    }
}
public class GravitationalParameter(double value) : PhysicalValue(value)
{

    public static readonly GravitationalParameter EarthGravitationalParameter =
    new GravitationalParameter(3.986004418e14);

    public static readonly GravitationalParameter SunGravitationalParameter =
    new GravitationalParameter(3.986004418e14);

    public static GravitationalParameter FromMasses(
        Mass central,
        Mass orbiting
    )
    {
        var value =
            new GravitationalConstant().Value
            * (central.Value + orbiting.Value);

        return new GravitationalParameter(value);
    }


}