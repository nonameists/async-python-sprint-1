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

    calc_data_service = DataCalculationTask(cities_forecasts)
    calculated_data = calc_data_service.get_calculated_data()

    analyzer_data_service = DataAnalyzingTask(calculated_data)
    analyzed_data = analyzer_data_service.analyze_data()

    aggregation_service = DataAggregationTask(analyzed_data)
    aggregation_service.save_data_to_csv()

    print(f"Самый удачный город для посещения это - {analyzer_data_service.main_town}")


if __name__ == "__main__":
    forecast_weather()
