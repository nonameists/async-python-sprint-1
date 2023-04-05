from typing import List, Optional

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


class CityDayWeatherModel(BaseModel):
    date: str
    average_temp: float
    good_weather_hours: int


class CalculatedCityWeatherDataModel(BaseModel):
    city_name: str
    days: List[CityDayWeatherModel]
    total_average_temp: float
    total_average_good_weather_hours: float
    rating: Optional[int]

    def get_avg_temp_data(self) -> List[float]:
        """Метод модели возвращает список средних температур по всем дням."""
        result = [day.average_temp for day in self.days]
        return result

    def get_all_good_weather_hours(self) -> List[float]:
        """Метод модели возвращает список кол-ва ясных часов по всем дням."""
        result = [day.good_weather_hours for day in self.days]
        return result
