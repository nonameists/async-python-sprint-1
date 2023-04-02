from typing import List

from pydantic import BaseModel, validator

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
