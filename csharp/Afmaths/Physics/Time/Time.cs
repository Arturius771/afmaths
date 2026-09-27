namespace Afmaths;

public class Epoch
{
    public Time StartOfEpoch { get; }

    public Epoch(Time startOfEpoch)
    {
        StartOfEpoch = startOfEpoch;
    }
}
public class Time(double value) : PhysicalValue<Time>(value)
{
    public static readonly Second SECONDS_PER_DAY = new Second(86400);
    public static readonly Minute MINUTES_PER_DAY = new Minute(1440);
    public static readonly Hour HOURS_PER_DAY = new Hour(24);
    public static readonly Second SECONDS_PER_HOUR = new Second(3600);
    public static readonly Second SECONDS_PER_MINUTE = new Second(60);

    public static readonly Minute MINUTES_PER_HOUR = new Minute(60);

    public Time(Second value) : this(value.Value)
    {

    }
    public Time(Minute value) : this(value.Value * SECONDS_PER_MINUTE.Value)
    {

    }
    public Time(Hour value) : this(value.Value * SECONDS_PER_HOUR.Value)
    {

    }
    public Time(Day value) : this(value.Value * SECONDS_PER_DAY.Value)
    {

    }
    protected override Time Create(double value) => new(value);

    public Minute AsMinutes => new Minute(Value / SECONDS_PER_MINUTE.Value);

    public Hour AsHours => new Hour(Value / SECONDS_PER_HOUR.Value);

    public Day AsDays => new Day(Value / SECONDS_PER_DAY.Value);

    public new Time Delta(Time other)
    {
        return new Time(Value - other.Value);
    }
}

public class Second(double value) : Time(value)
{
    protected override Second Create(double value) => new(value);
}

public class Minute(double value) : Time(value)
{
    protected override Minute Create(double value) => new(value);
}

public class Hour(double value) : Time(value)
{
    protected override Hour Create(double value) => new(value);
}

public class Day(double value) : Date(value)
{
    protected override Day Create(double value) => new(value);
}

public class Month(double value) : Date(value)
{
    protected override Month Create(double value) => new(value);
}

public class Year(double value) : Date(value)
{
    protected override Year Create(double value) => new(value);
}

public class Date(double value) : PhysicalValue<Date>(value)
{
    protected override Date Create(double value) => new(value);
}

public class JulianDate(double value) : Date(value)
{
    protected override JulianDate Create(double value) => new(value);
}