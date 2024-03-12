from datetime import datetime
import math

# Credit: http://www.stargazing.net/kepler/altaz.html

def days_since_j2000() -> int:
  # Set the date and time
  date_time_str = "2000-01-01 12:00:00"
  date_time_format = "%Y-%m-%d %H:%M:%S"
  date_time = datetime.strptime(date_time_str, date_time_format)

  # Calculate the Julian Date for the given date and time
  jd_epoch = 2451545.0  # J2000.0 epoch
  jd_date_time = jd_epoch + (date_time - datetime(2000, 1, 1, 12, 0, 0)).total_seconds() / (24 * 3600)

  # Calculate the number of days from J2000
  days_from_j2000 = jd_date_time - jd_epoch
  return days_from_j2000

def universal_time_in_decimal_hours():
  time = str(datetime.utcnow().strftime("%H:%M:%S"))

  (h,m,_) = time.split(':')

  UT = int(h)+(int(m) / 60)

  print(f"Universal time: {UT}")
  return UT

def calculate_local_sidereal_time(days, long, ut):
  lst = 100.46 + 0.985647 * days + long + 15 * ut

  if(lst < 0):
    lst = lst + 360
  if(lst > 360):
    lst = lst - 360

  print(f"Local Sidereal Time: {lst}")
  return lst

def calculate_hour_angle(lst, ra):
  hour_angle = lst - ra
  print(lst, ra)
  if(hour_angle < 0):
    hour_angle = hour_angle + 360
  if(hour_angle > 360):
    hour_angle = hour_angle - 360

  print(f"Hour angle: {hour_angle}")
  return hour_angle

def convert_right_ascension_input_to_decimal_degrees(right_ascension):
  (h,m,s) = right_ascension.split(':')
  return (int(h)+(float(m)/60)+(float(s)/3600)) * 15

print("Manually enter days? (enter true/false):")
if(input() == "true"):
  print("Enter the number of j2000 days")
  DAYS = float(input())
else:
  DAYS = days_since_j2000()  
print("Manually enter UT(decimal hour)? (enter true/false):")
if(input() == "true"):
  print("Enter the decimal hour")
  UT = float(input())
else:
  UT =  universal_time_in_decimal_hours()
print("Enter your longitude (decimal degrees):")
LONG = float(input())
print("Enter your latitude (decimal degrees):")
LAT = float(input())
LST = calculate_local_sidereal_time(DAYS, LONG, UT)
print("Right Ascension in decimal? (enter true/false):")
if(input() == "true"):
  print("Enter the Right Ascension(decimal degrees):")
  RA = float(input())
else:
  print("Enter the Right Ascension(h:m):")
  RA = convert_right_ascension_input_to_decimal_degrees(input())
HA = calculate_hour_angle(LST, RA)
print("Enter the Declination:")
DEC = float(input())

sin_dec = math.sin(math.radians(DEC))
sin_lat = math.sin(math.radians(LAT))
cos_dec = math.cos(math.radians(DEC))
cos_lat = math.cos(math.radians(LAT))
cos_ha = math.cos(math.radians(HA))

ALT = math.degrees(math.asin(sin_dec*sin_lat+cos_dec*cos_lat*cos_ha))

sin_alt = math.sin(math.radians(ALT))
cos_alt = math.cos(math.radians(ALT))
sin_ha = math.sin(math.radians(HA))

cos_A = (sin_dec - sin_alt * sin_lat)/(cos_alt * cos_lat)
A = math.degrees(math.acos(cos_A))

if(math.degrees(sin_ha) < 0):
  AZ = A
else:
  AZ = 360 - A

print(f"Altitude: {ALT}")
print(f"Azimuth: {AZ}")