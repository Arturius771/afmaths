import datetime
import math

from astronomy_types import (
    DMS,
    HMS,
    T,
    Anomaly,
    Coordinate2D,
    Coordinate3D,
    Date,
    Day,
    DecimalTime,
    Degrees,
    EccentricAnomaly,
    FullDate,
    Hour,
    Minute,
    Month,
    Position,
    PositionVector,
    Radians,
    Scalar,
    Second,
    StateVector,
    Time,
    TrueAnomaly,
    Vector2D,
    Vector3D,
    Velocity,
    VelocityVector,
    Year,
)


# region Factories
def make_vector2d(x: T, y: T) -> Vector2D[T]:
    return Vector2D(x, y)


def make_vector3d(
    x: T,
    y: T,
    z: T,
) -> Vector3D[T]:
    return Vector3D(x, y, z)


def make_date(year: Year, month: Month, day: Day) -> Date:
    return Date(Year(year), Month(month), Day(Scalar(day)))


def make_time(hms: HMS) -> Time:
    return Time(
        hour=Hour(hms.hours),
        minute=Minute(hms.minutes),
        second=Second(Scalar(hms.seconds)),
    )


def make_state_vector(pos: PositionVector, vel: VelocityVector) -> StateVector:
    return StateVector(pos, vel)


def make_true_anomaly(val: float) -> TrueAnomaly:
    return TrueAnomaly(Anomaly(Radians(Scalar(val))))


def make_eccentric_anomaly(val: float) -> EccentricAnomaly:
    return EccentricAnomaly(Anomaly(Radians(Scalar(val))))


# region Type Conversion


def radians_from_degrees(degrees: Degrees) -> Radians:
    return Radians(Scalar(math.radians(float(degrees))))


def radians_from_string(degrees_str: str) -> Radians:
    return Radians(Scalar(float(math.radians(float(degrees_str)))))


def radians_from_dms(dms: DMS) -> Radians:
    return radians_from_degrees(degrees_from_dms(dms))


def radians_from_hms(hms: HMS) -> Radians:
    return radians_from_degrees(degrees_from_hms(hms))


def degrees_from_radians(radians: Radians) -> Degrees:
    return Degrees(Scalar(math.degrees(radians)))


def degrees_from_dms(dms: DMS) -> Degrees:
    sign = -1 if dms.degrees < 0 else 1
    return Degrees(
        Scalar(sign * (abs(dms.degrees) + dms.minutes / 60 + dms.seconds / 3600))
    )


def degrees_from_hms(hms: HMS) -> Degrees:
    return Degrees(Scalar(15 * (hms.hours + hms.minutes / 60 + hms.seconds / 3600)))


def degrees_from_hours(hours: DecimalTime) -> Degrees:
    return Degrees(Scalar(float(hours) * 15))


def hours_from_degrees(degrees: Degrees) -> DecimalTime:
    return DecimalTime(Scalar(float(degrees) / 15))


def decimal_time_from_time(time: Time) -> DecimalTime:
    unsigned_decimal = (
        int(time.hour) + int(time.minute) / 60 + float(time.second) / 3600
    )

    return DecimalTime(Scalar(unsigned_decimal))


def time_from_decimal_time(time: DecimalTime) -> Time:
    unsigned_decimal = abs(float(time))

    total_seconds = unsigned_decimal * 3600
    rounded_seconds = round(total_seconds % 60, 2)

    seconds = 0 if rounded_seconds == 60 else rounded_seconds
    remainder = total_seconds + 60 if rounded_seconds == 60 else total_seconds

    minutes = math.floor(remainder / 60) % 60
    hours = math.floor(remainder / 3600)

    return Time(
        Hour(hours),
        Minute(minutes),
        Second(Scalar(seconds)),
    )


def fulldate_from_python_datetime(date: datetime.datetime) -> FullDate:
    return FullDate(
        date=make_date(
            year=Year(date.year), month=Month(date.month), day=Day(Scalar(date.day))
        ),
        time=make_time(HMS(hours=date.hour, minutes=date.minute, seconds=date.second)),
    )


def string_from_fulldate(date: FullDate) -> str:
    return f"{date.date.year:04d}-{date.date.month:02d}-{date.date.day:02d} {date.time.hour:02d}:{date.time.minute:02d}:{date.time.second:02d}"


def seconds_from_python_timedelta(delta: datetime.timedelta) -> Second:
    return Second(Scalar(delta.total_seconds()))


def hours_from_seconds(seconds: Second) -> Hour:
    return Hour(int(round(float(seconds) / 3600)))


def hour_string_from_hour(hour: Hour) -> str:
    return f"{hour:02d}h"


def vector2d_from_coordinate2d(coordinates: Coordinate2D) -> Vector2D[Scalar]:
    return make_vector2d(coordinates.x, coordinates.y)


def vector3d_from_coordinate3d(coordinates: Coordinate3D) -> Vector3D[Scalar]:
    return make_vector3d(coordinates.x, coordinates.y, coordinates.z)


def vector3d_from_position(position_vector: PositionVector) -> Vector3D[Scalar]:
    return make_vector3d(position_vector.x, position_vector.y, position_vector.z)


def vector3d_from_velocity(velocity_vector: VelocityVector) -> Vector3D[Scalar]:
    return make_vector3d(velocity_vector.x, velocity_vector.y, velocity_vector.z)


def velocity_from_vector(vector: Vector3D) -> VelocityVector:
    return VelocityVector(Velocity(vector.x), Velocity(vector.y), Velocity(vector.z))


def position_from_vector(vector: Vector3D) -> PositionVector:
    return PositionVector(Position(vector.x), Position(vector.y), Position(vector.z))


def coordinate3d_from_vector(vector: Vector3D) -> Coordinate3D:
    return Coordinate3D(vector.x, vector.y, vector.z)


def coordinate2d_from_vector(vector: Vector2D) -> Coordinate2D:
    return Coordinate2D(vector.x, vector.y)
