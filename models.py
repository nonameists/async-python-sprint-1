from typing import List, Optional

from pydantic import BaseModel, validator, conlist

from config import WEATHER_CONDITIONS


class ForecastHoursModel(BaseModel):
    hour: int
    temp: int
    condition: str

    @validator("condition")
    def validate_condition(cls, value: str) -> str:
        if value not in WEATHER_CONDITIONS:
            raise ValueError("Condition not found!")
        return value


class CityForecastDataModel(BaseModel):
    date: str
    hours: List[ForecastHoursModel]


class CityWeatherDataModel(BaseModel):
    city_name: str
    forecasts: List[CityForecastDataModel]


class CityDayWeatherModel(BaseModel):
    date: str
    average_temp: float
    good_weather_hours: int


class CalculatedCityWeatherDataModel(BaseModel):
    city_name: str
    days: List[CityDayWeatherModel]
    total_average_temp: float
    total_average_good_weather_hours: float
