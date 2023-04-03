# import logging
# import threading
# import subprocess
# import multiprocessing

from api_client import YandexWeatherAPI
from tasks import (
    DataFetchingTask,
    DataCalculationTask,
    DataAggregationTask,
    DataAnalyzingTask,
)
from utils import CITIES


def forecast_weather():
    """
    Анализ погодных условий по городам
    """
    cities = list(CITIES)
    fetch_data_service = DataFetchingTask(cities)
    cities_forecasts = fetch_data_service.fetch_forecasts()
    pass


if __name__ == "__main__":
    forecast_weather()
