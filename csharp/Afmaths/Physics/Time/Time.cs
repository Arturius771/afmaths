namespace Afmaths;

/// <summary>
/// Represents an epoch, which is a specific point in time used as a reference for astronomical and physical calculations.
/// </summary>
public class Epoch
{
    public Time StartOfEpoch { get; }

    public Epoch(Time startOfEpoch)
    {
        StartOfEpoch = startOfEpoch;
    }
}

/// <summary>
/// Represents a point in time, measured in seconds, and provides conversions to various time units.
/// </summary>
/// <param name="value">The time value in seconds.</param>
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

/// <summary>
/// Represents a time value in seconds.
/// </summary>
public class Second(double value) : Time(value)
{
    protected override Second Create(double value) => new(value);
}

/// <summary>
/// Represents a time value in minutes.
/// </summary>
public class Minute(double value) : Time(value)
{
    protected override Minute Create(double value) => new(value);
}

/// <summary>
/// Represents a time value in hours.
/// </summary>
public class Hour(double value) : Time(value)
{
    protected override Hour Create(double value) => new(value);
}

/// <summary>
/// Represents a calendar-based time unit, such as days, months, or years.
/// </summary>
/// <typeparam name="T">The specific type of the calendar time unit.</typeparam>
/// <param name="value">The value of the calendar time unit.</param>
public abstract class CalendarTimeUnit<T>(double value) : PhysicalValue<T>(value)
    where T : CalendarTimeUnit<T>
{
    public Time AsTime => CreateTime();

    protected abstract Time CreateTime();
}
/// <summary>
/// Represents a day as a calendar-based time unit.
/// </summary>
/// <param name="value">The number of days.</param>
public class Day(double value) : CalendarTimeUnit<Day>(value)
{
    protected override Day Create(double value) => new(value);

    protected override Time CreateTime() => new Time(this);
}

/// <summary>
/// Represents a month as a calendar-based time unit.
/// </summary>
/// <param name="value">The number of months.</param>
public class Month(double value) : CalendarTimeUnit<Month>(value)
{
    protected override Month Create(double value) => new(value);

    protected override Time CreateTime() => new Time(this);
}

/// <summary>
/// Represents a year as a calendar-based time unit.
/// </summary>
/// <param name="value">The number of years.</param>
public class Year(double value) : CalendarTimeUnit<Year>(value)
{
    protected override Year Create(double value) => new(value);

    protected override Time CreateTime() => new Time(this);
}

/// <summary>
/// Represents a specific point in time, including the year, month, day, hour, minute, and second.
/// </summary>
/// <param name="year">The year component of the date and time.</param>
/// <param name="month">The month component of the date and time.</param>
/// <param name="day">The day component of the date and time.</param>
/// <param name="hour">The hour component of the date and time.</param>
/// <param name="minute">The minute component of the date and time.</param>
/// <param name="second">The second component of the date and time.</param>
public class DateTime
{
    public Year Year { get; }
    public Month Month { get; }
    public Day Day { get; }
    public Hour Hour { get; }
    public Minute Minute { get; }
    public Second Second { get; }

    /// <summary>
    /// Initializes a new instance of the <see cref="DateTime"/> class with the specified year, month, day, hour, minute, and second.
    /// </summary>
    /// <param name="year">The year component of the date and time.</param>
    /// <param name="month">The month component of the date and time.</param>
    /// <param name="day">The day component of the date and time.</param>
    /// <param name="hour">The hour component of the date and time.</param>
    /// <param name="minute">The minute component of the date and time.</param>
    /// <param name="second">The second component of the date and time.</param>
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

/// <summary>
/// Represents a Julian date, which is a continuous count of days since the beginning of the Julian period.
/// </summary>
/// <param name="value">The Julian date value.</param>
public class JulianDate(double value) : Day(value)
{
    protected override JulianDate Create(double value) => new(value);
}