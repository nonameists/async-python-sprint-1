

import pytest

from tasks import DataFetchingTask, DataCalculationTask, DataAnalyzingTask


@pytest.fixture()
def cities():
    return ["MOSCOW", "PARIS", "BEIJING"]


@pytest.fixture()
def cities_forecast(cities):
    fetch_data_service = DataFetchingTask(cities)
    cities_forecasts = fetch_data_service.fetch_forecasts()
    return cities_forecasts


@pytest.fixture()
def cities_forecasts_names(cities_forecast):
    return [city.city_name for city in cities_forecast]


@pytest.fixture()
def calculated_data(cities_forecast):
    calc_data_service = DataCalculationTask(cities_forecast)
    calculated_data = calc_data_service.get_calculated_data()
    return calculated_data


@pytest.fixture()
def calculated_avg_temp(calculated_data):
    return [city.total_average_temp for city in calculated_data]


@pytest.fixture()
def calculated_good_weather_hours_temp(calculated_data):
    return [city.total_average_good_weather_hours for city in calculated_data]


@pytest.fixture()
def analyzed_data(calculated_data):
    analyzer_data_service = DataAnalyzingTask(calculated_data)
    analyzed_data = analyzer_data_service.analyze_data()
    return analyzed_data


@pytest.fixture()
def city_ratings(analyzed_data):
    return [city.rating for city in analyzed_data]

