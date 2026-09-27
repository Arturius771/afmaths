using Xunit;

namespace Afmaths.Tests;

public class TimeTests
{
    [Fact]
    public void TimeConstants_HaveExpectedValues()
    {
        Assert.Equal(86400, Time.SECONDS_PER_DAY.Value);
        Assert.Equal(1440, Time.MINUTES_PER_DAY.Value);
        Assert.Equal(24, Time.HOURS_PER_DAY.Value);
        Assert.Equal(3600, Time.SECONDS_PER_HOUR.Value);
        Assert.Equal(60, Time.SECONDS_PER_MINUTE.Value);
        Assert.Equal(60, Time.MINUTES_PER_HOUR.Value);
    }

    [Fact]
    public void Time_FromSeconds_UsesSecondsAsBaseUnit()
    {
        var result = new Time(new Second(90));

        Assert.Equal(90, result.Value);
    }

    [Fact]
    public void Time_FromMinutes_ConvertsToSeconds()
    {
        var result = new Time(new Minute(2));

        Assert.Equal(120, result.Value);
    }

    [Fact]
    public void Time_FromHours_ConvertsToSeconds()
    {
        var result = new Time(new Hour(2));

        Assert.Equal(7200, result.Value);
    }

    [Fact]
    public void Time_FromDays_ConvertsToSeconds()
    {
        var result = new Time(new Day(2));

        Assert.Equal(172800, result.Value);
    }

    [Fact]
    public void AsMinutes_ConvertsSecondsToMinutes()
    {
        var time = new Time(120);

        var result = time.AsMinutes;

        Assert.Equal(2, result.Value);
    }

    [Fact]
    public void AsHours_ConvertsSecondsToHours()
    {
        var time = new Time(7200);

        var result = time.AsHours;

        Assert.Equal(2, result.Value);
    }

    [Fact]
    public void AsDays_ConvertsSecondsToDays()
    {
        var time = new Time(172800);

        var result = time.AsDays;

        Assert.Equal(2, result.Value);
    }

    [Fact]
    public void Delta_ReturnsDifferenceInSeconds()
    {
        var first = new Time(120);
        var second = new Time(45);

        var result = first.Delta(second);

        Assert.Equal(75, result.Value);
    }



    [Fact]
    public void Delta_ReturnsCorrectTimeWhenComparingDifferentUnits()
    {
        var first = new Time(new Minute(2));
        var second = new Time(new Second(30));

        var result = first.Delta(second);

        Assert.Equal(90, result.Value);


        var third = new Time(new Day(2));
        var fourth = new Time(new Hour(32.5));

        var otherResult = third.Delta(fourth);

        Assert.Equal(55800, otherResult.Value);
    }

    [Fact]
    public void Delta_CanReturnNegativeTime()
    {
        var first = new Time(45);
        var second = new Time(120);

        var result = first.Delta(second);

        Assert.Equal(-75, result.Value);
    }

    [Fact]
    public void Second_StoresValueAsSeconds()
    {
        var result = new Second(30);

        Assert.Equal(30, result.Value);
    }

    [Fact]
    public void Minute_InheritsTimeBehavior()
    {
        var result = new Minute(2);

        Assert.Equal(2, result.Value);
    }

    [Fact]
    public void Hour_InheritsTimeBehavior()
    {
        var result = new Hour(2);

        Assert.Equal(2, result.Value);
    }

    [Fact]
    public void Day_InheritsTimeBehavior()
    {
        var result = new Day(2);

        Assert.Equal(2, result.Value);
    }

    [Fact]
    public void Minute_CanBeConvertedToTimeInSeconds()
    {
        var minute = new Minute(1);

        var result = new Time(minute);

        Assert.Equal(60, result.Value);
    }

    [Fact]
    public void Hour_CanBeConvertedToTimeInSeconds()
    {
        var hour = new Hour(1);

        var result = new Time(hour);

        Assert.Equal(3600, result.Value);
    }

    [Fact]
    public void Day_CanBeConvertedToTimeInSeconds()
    {
        var day = new Day(1);

        var result = new Time(day);

        Assert.Equal(86400, result.Value);
    }

    [Fact]
    public void TimeConversion_RoundTripPreservesValue()
    {
        var original = new Time(98765.4321);

        var result = new Time(original.AsDays);

        Assert.Equal(original.Value, result.Value, 10);
    }
}