import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import List, Dict, Optional, Iterator

from api_client import YandexWeatherAPI
from config import logger, GOOD_WEATHER_CONDITIONS
from models import CityWeatherDataModel, CalculatedCityWeatherDataModel, CityDayWeatherModel


class DataFetchingTask:
    api_client = YandexWeatherAPI()

    def __init__(self, cities: List[str]) -> None:
        self.cities = cities

    def fetch_forecasts(self) -> List[CityWeatherDataModel]:
        """
        Загрузка данных. Использует YandexWeatherAPI для получения данных.
        """
        logger.info("Начинаем забирать данные по городам")

        with ThreadPoolExecutor(max_workers=os.cpu_count() + 4) as pool:
            raw_cities_data_response = pool.map(
                self._fetch_city_forecast_data, self.cities
            )

        cities_forecast_data = self._validate_raw_data(raw_cities_data_response)
        logger.info("Загрузка данных по городам завершена")
        return cities_forecast_data

    def _fetch_city_forecast_data(self, city_name: str) -> Optional[Dict]:
        """Внутренний метод для получения 'сырых' данных от API"""
        try:
            raw_city_data = self.api_client.get_forecasting(city_name)
            # добавляем новый ключ city_name который нам понадобится
            # при валидации данных в моделе CityWeatherDataModel
            raw_city_data.update({"city_name": city_name})
            return raw_city_data
        except Exception as fetch_error:
            logger.error(
                f"Произошла ошибка {fetch_error} во время загрузки данных"
            )

    def _validate_raw_data(self, raw_cities_data_response: Iterator[Dict | None]) -> List[CityWeatherDataModel]:
        """Внутренний метод валидации 'сырых' данных."""
        validated_result = []
        for city_data in raw_cities_data_response:
            if city_data is None:
                continue
            try:
                data = CityWeatherDataModel(**city_data)
                validated_result.append(data)
            except ValueError as value_error:
                logger.error(
                    f"Произошла ошибка {value_error} во время валидации данных"
                    f" в моделе CityWeatherDataModel"
                )
                continue

        return validated_result


class DataCalculationTask:
    MIN_HOUR = 9
    MAX_HOUR = 19

    def __init__(self, cities_forecasts: List[CityWeatherDataModel]) -> None:
        self.cities_forecasts = cities_forecasts

    def get_calculated_data(self) -> List[CalculatedCityWeatherDataModel]:
        """Публичный метод запуска просчета данных по городам."""
        with ProcessPoolExecutor() as pool:
            raw_result = pool.map(self._calculate_data, self.cities_forecasts)
        result = [CalculatedCityWeatherDataModel(**raw_city_result) for raw_city_result in raw_result]
        return result

    def _calculate_data(self, city_data: CityWeatherDataModel) -> Dict:
        """Внутренний метод вычисления значений по городую."""
        hours_period = self.MAX_HOUR - self.MIN_HOUR

        city_data_forecast = {
            "city_name": city_data.city_name,
            "days": []
        }
        total_days_temp = 0
        total_hours_good_weather = 0
        days = 0

        for forecast in city_data.forecasts:
            logger.info(f"Начинаем считать данные для даты: {forecast.date} г.{city_data.city_name}")
            forecast_data = {
                "date": forecast.date,
            }
            total_temp = 0
            good_weather_hours = 0
            days += 1
            # если нет данных по времени идем на другой день
            if len(forecast.hours) == 0:
                continue
            for item in forecast.hours:
                if self.MIN_HOUR <= item.hour <= self.MAX_HOUR:
                    total_temp += item.temp
                    if item.condition in GOOD_WEATHER_CONDITIONS:
                        good_weather_hours += 1
            days_avg_temp = total_temp/hours_period
            forecast_data["average_temp"] = round(days_avg_temp, 1)
            forecast_data["good_weather_hours"] = good_weather_hours
            city_data_forecast["days"].append(forecast_data)

            total_days_temp += days_avg_temp
            total_hours_good_weather += good_weather_hours

        city_data_forecast["total_average_temp"] = round(total_days_temp/days, 1)
        city_data_forecast["total_average_good_weather_hours"] = round(total_hours_good_weather/days, 1)
        logger.info(f"Подсчет закончен для г.{city_data.city_name}")

        return city_data_forecast


class DataAggregationTask:
    pass


class DataAnalyzingTask:
    pass
