import logging

WEATHER_CONDITIONS = {
    "clear", "partly-cloudy", "cloudy", "overcast", "drizzle", "light-rain",
    "rain", "moderate-rain", "heavy-rain", "continuous-heavy-rain", "showers",
    "wet-snow", "light-snow", "snow", "snow-showers", "hail", "thunderstorm",
    "thunderstorm-with-rain", "thunderstorm-with-hail"
}

GOOD_WEATHER_CONDITIONS = {
    "clear", "partly-cloudy", "cloudy", "overcast",
}

logger_format = "%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"

logging.basicConfig(
    filename="logfile.log",
    filemode="a",
    format=logger_format,
    level=logging.INFO
)

logger = logging.getLogger()

CSV_FILE_NAME = "city_data_table.csv"