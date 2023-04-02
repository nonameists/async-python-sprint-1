import logging

WEATHER_CONDITIONS = {
    "clear", "partly-cloudy", "cloudy", "overcast", "drizzle", "light-rain",
    "rain", "moderate-rain", "heavy-rain", "continuous-heavy-rain", "showers",
    "wet-snow", "light-snow", "snow", "snow-showers", "hail", "thunderstorm",
    "thunderstorm-with-rain", "thunderstorm-with-hail"
}

logger_format = "%(levelname)s %(filename)s %(asctime)s - %(message)s"

logging.basicConfig(
    filename="logfile.log",
    filemode="a",
    format=logger_format,
    level=logging.INFO
)

logger = logging.getLogger()
