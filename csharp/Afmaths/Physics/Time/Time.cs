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

    public static readonly Second SECONDS_PER_YEAR = new Second(31536000);
    /// <summary>
    /// Converts a Year value to an approximately equivalent Time representation in seconds.
    /// </summary>
    /// <remarks>
    /// This approximation assumes a non-leap year with 365 days.
    /// </remarks>
    public static readonly Second SECONDS_PER_MONTH = new Second(SECONDS_PER_YEAR.Value / 12);

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
    /// <summary>
    /// Converts a Month value to an approximately equivalent Time representation in seconds.
    /// </summary>
    /// <param name="value"></param>
    public Time(Month value) : this(value.Value * SECONDS_PER_MONTH.Value)
    {
    }
    public Time(Year value) : this(value.Value * SECONDS_PER_YEAR.Value)
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

public abstract class CalendarTimeUnit<T>(double value) : PhysicalValue<T>(value)
    where T : CalendarTimeUnit<T>
{
    public Time AsTime => CreateTime();

    protected abstract Time CreateTime();
}
public class Day(double value) : CalendarTimeUnit<Day>(value)
{
    protected override Day Create(double value) => new(value);

    protected override Time CreateTime() => new Time(this);
}

public class Month(double value) : CalendarTimeUnit<Month>(value)
{
    protected override Month Create(double value) => new(value);

    protected override Time CreateTime() => new Time(this);
}

public class Year(double value) : CalendarTimeUnit<Year>(value)
{
    protected override Year Create(double value) => new(value);

    protected override Time CreateTime() => new Time(this);
}

public class DateTime
{
    public Year Year { get; }
    public Month Month { get; }
    public Day Day { get; }
    public Hour Hour { get; }
    public Minute Minute { get; }
    public Second Second { get; }
    public DateTime(Year year, Month month, Day day, Hour hour, Minute minute, Second second)
    {
        Year = year;
        Month = month;
        Day = day;
        Hour = hour;
        Minute = minute;
        Second = second;
    }
}

public class JulianDate(double value) : Day(value)
{
    protected override JulianDate Create(double value) => new(value);
}