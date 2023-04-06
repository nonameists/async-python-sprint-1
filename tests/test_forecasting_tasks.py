from pathlib import Path
import os

import pytest

from config import CSV_FILE_NAME
from tasks import DataFetchingTask, DataCalculationTask, DataAnalyzingTask, DataAggregationTask


class BaseTearDown:

    def teardown_method(self):
        """Remove logs and csv file."""
        log_file_path = os.path.join(Path(__file__).resolve().parent.parent, "logfile.log")
        csv_file_path = os.path.join(Path(__file__).resolve().parent.parent, CSV_FILE_NAME)
        if os.path.exists(log_file_path):
            os.remove(log_file_path)
        if os.path.exists(csv_file_path):
            os.remove(csv_file_path)


class TestFetchTask(BaseTearDown):

    def test_forecast_fetching_amount(self, cities):
        fetch_data_service = DataFetchingTask(cities)
        cities_forecasts = fetch_data_service.fetch_forecasts()
        assert len(cities_forecasts) == len(cities), "Ответ содержит неверное количество элементов"

    def test_forecast_fetching_amount_of_days(self, cities_forecast):
        for city in cities_forecast:
            assert len(city.forecasts) == 5, "Количество дней по которым есть информация не совпадает"

    @pytest.mark.parametrize("city", ["MOSCOW", "PARIS", "BEIJING"])
    def test_forecast_fetching_city_names(self, city, cities_forecasts_names):
        assert city in cities_forecasts_names, f"Город {city} не найден в списке"


class TestCalculationTask(BaseTearDown):

    def test_calculated_data(self, cities_forecast):
        calc_data_service = DataCalculationTask(cities_forecast)
        calculated_data = calc_data_service.get_calculated_data()
        assert calculated_data, "Нет просчитанных данных"
        assert len(calculated_data) == 3, "Количество просчитанных городов не совпадает"

    @pytest.mark.parametrize("city_avg_temp", [9.7, 11.4, 25.0])
    def test_avg_temp(self, city_avg_temp, calculated_avg_temp):
        assert city_avg_temp in calculated_avg_temp, "Средняя температура не совпадает"

    @pytest.mark.parametrize("city_good_weather_hours", [1.6, 6.2, 7.8])
    def test_cities_good_weather_hours(self, city_good_weather_hours, calculated_good_weather_hours_temp):
        a=calculated_good_weather_hours_temp
        assert city_good_weather_hours in calculated_good_weather_hours_temp, "Количество ясных часов не совпадает"


class TestAnalyzingTask(BaseTearDown):

    def test_analyzed_data(self, calculated_data):
        analyzer_data_service = DataAnalyzingTask(calculated_data)
        analyzed_data = analyzer_data_service.analyze_data()
        assert analyzed_data, "Нет проанализированных данных"
        assert len(analyzed_data) == 3, "Количество проанализированных городов не совпадает"
        assert analyzer_data_service.main_town == "BEIJING", "Наилучший город не совпадает"

    @pytest.mark.parametrize("city_rating", [1, 2, 3])
    def test_city_ratings(self, city_rating, city_ratings):
        assert city_rating in city_ratings, "Рейтинг не совпадает"


class TestAggregationTask(BaseTearDown):

    def test_csv_file_creation(self, analyzed_data):
        aggregation_service = DataAggregationTask(analyzed_data)
        aggregation_service.save_data_to_csv()
        csv_file_path = os.path.join(Path(__file__).resolve().parent.parent, CSV_FILE_NAME)
        is_exist = os.path.exists(csv_file_path)
        assert is_exist, "CSV файл не создался"





