import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional

from api_client import YandexWeatherAPI
from config import logger
from models import CityWeatherDataModel


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
        try:
            cities_forecast_data = [
                CityWeatherDataModel(**city_data)
                for city_data in raw_cities_data_response
                if city_data is not None
            ]
            logger.info("Загрузка данных по городам завершена")
            return cities_forecast_data
        except ValueError as value_error:
            logger.error(
                f"Произошла ошибка {value_error} во время валидации данных"
                f" в моделе CityWeatherDataModel "
            )

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


class DataCalculationTask:
    pass


class DataAggregationTask:
    pass


class DataAnalyzingTask:
    pass
