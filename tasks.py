import csv
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from threading import Lock
from typing import List, Dict, Optional, Iterator, Tuple

from api_client import YandexWeatherAPI
from config import logger, GOOD_WEATHER_CONDITIONS, CSV_FILE_NAME
from models import (
    CityWeatherDataModel,
    CalculatedCityWeatherDataModel,
)


class DataFetchingTask:
    api_client = YandexWeatherAPI()

    def __init__(self, cities: List[str]) -> None:
        self.cities = cities

    def fetch_forecasts(self) -> List[CityWeatherDataModel]:
        """
        Загрузка данных. Использует YandexWeatherAPI для получения данных.
        """
        logger.info("Начинаем забирать данные по городам")

        with ThreadPoolExecutor() as pool:
            raw_cities_data_response = pool.map(
                self._fetch_city_forecast_data, self.cities
            )

        cities_forecast_data = self._validate_raw_data(
            raw_cities_data_response
        )
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

    def _validate_raw_data(
        self, raw_cities_data_response: Iterator[Dict | None]
    ) -> List[CityWeatherDataModel]:
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
        result = [
            CalculatedCityWeatherDataModel(**raw_city_result)
            for raw_city_result in raw_result
        ]
        return result

    def _calculate_data(self, city_data: CityWeatherDataModel) -> Dict:
        """Внутренний метод вычисления значений по городую."""
        hours_period = self.MAX_HOUR - self.MIN_HOUR

        city_data_forecast = {"city_name": city_data.city_name, "days": []}
        total_days_temp = 0
        total_hours_good_weather = 0
        days = 0

        for forecast in city_data.forecasts:
            logger.info(
                f"Начинаем считать данные для даты: {forecast.date} г.{city_data.city_name}"
            )
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
            days_avg_temp = total_temp / hours_period
            forecast_data["average_temp"] = round(days_avg_temp, 1)
            forecast_data["good_weather_hours"] = good_weather_hours
            city_data_forecast["days"].append(forecast_data)

            total_days_temp += days_avg_temp
            total_hours_good_weather += good_weather_hours

        city_data_forecast["total_average_temp"] = round(
            total_days_temp / days, 1
        )
        city_data_forecast["total_average_good_weather_hours"] = round(
            total_hours_good_weather / days, 1
        )
        logger.info(f"Подсчет закончен для г.{city_data.city_name}")

        return city_data_forecast


class DataAnalyzingTask:
    def __init__(
        self, calculated_cities_data: List[CalculatedCityWeatherDataModel]
    ) -> None:
        self.data = calculated_cities_data
        self.main_town = None

    def analyze_data(self) -> List[CalculatedCityWeatherDataModel]:
        """Метод для запуска сортировки городов, выставления рейтинга и записи наилучшего города."""
        self._sort_data_by_temp_and_weather()
        self._set_rating_to_cities()
        self._set_main_town()

        return self.data

    def _sort_data_by_temp_and_weather(self) -> None:
        """Внутренний метод сортировки городов по температуре и 'хорошим' дням."""
        logger.info(
            "Запуск сортировки городов по средней температуре и погожих днях"
        )
        self.data = sorted(
            self.data,
            key=lambda x: [
                x.total_average_temp,
                x.total_average_good_weather_hours,
            ],
            reverse=True,
        )

    def _set_rating_to_cities(self) -> None:
        """Внутренний метод установки атрибута rating для городов."""
        logger.info("Запуск установки рейтингов для городов")
        for rating, city_data in enumerate(self.data, 1):
            city_data.rating = rating

    def _set_main_town(self) -> None:
        """Внутренний метод устанавлиев 'лучший' город для посещения среди отсортированных городов"""
        self.main_town = self.data[0].city_name


class DataAggregationTask:
    def __init__(self, data: List[CalculatedCityWeatherDataModel]) -> None:
        self.data = data
        self._locker = Lock()

    def save_data_to_csv(self) -> None:
        """Публичный метод сохранения данных в csv файл."""
        data_to_csv, csv_headers = self._prepare_data_to_csv()
        logger.info("Запуск импорта данных в csv файл")
        self._write_headers(csv_headers)

        with ThreadPoolExecutor() as pool:
            for row in data_to_csv:
                pool.submit(self._write_row_to_csv, row)
        logger.info(f"CSV файл {CSV_FILE_NAME} успешно создан")
        print(f"CSV файл {CSV_FILE_NAME} успешно создан")

    def _prepare_data_to_csv(self) -> Tuple[List, List]:
        """Внутренний метод подготовки данных для создания csv файла."""
        logger.info("Запуск подготовки данных для импорта в csv таблицу")
        headers = [
            "Город/день",
            "",
            *[city_day.date for city_day in self.data[0].days],
            "Среднее",
            "Рейтинг",
        ]

        data_to_csv = []

        for city in self.data:
            temp_data = [
                city.city_name,
                "Температура, среднее",
                *city.get_avg_temp_data(),
                city.total_average_temp,
                city.rating,
            ]
            data_to_csv.append(temp_data)
            good_hours_data = [
                "",
                "Без осадков, часов",
                *city.get_all_good_weather_hours(),
                city.total_average_good_weather_hours,
                "",
            ]
            data_to_csv.append(good_hours_data)

        return data_to_csv, headers

    def _write_row_to_csv(self, row: List) -> None:
        """Внутренний метод записи строк в csv файл. Поток блокируется перед записью строки."""
        with open(CSV_FILE_NAME, "a") as file:
            with self._locker:
                writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
                writer.writerow(row)

    def _write_headers(self, headers: List[str]) -> None:
        """Внутренний метод записи хедеров в csv файл. Используется режим 'w' для 'обнуления' файла."""
        with open(CSV_FILE_NAME, "w") as file:
            writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(headers)

