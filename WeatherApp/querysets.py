"""Переиспользуемые ORM-запросы и динамические фильтры для WeatherRecord."""

from django.db import models


class WeatherRecordQuerySet(models.QuerySet):
    """Набор специализированных выборок для модели погодных записей.

    Нужен для того, чтобы хранить query-логику рядом с моделью, но отдельно
    от бизнес-логики сервиса, и переиспользовать её в разных endpoint'ах.
    """

    def sunny(self):
        """Возвращает записи только с солнечными кодами погоды.

        Нужен для инкапсуляции часто используемого условия по `weather_code`,
        чтобы не дублировать его по всему приложению.

        Returns:
            WeatherRecordQuerySet: QuerySet, содержащий записи с `weather_code` 0 и 1.
        """

        return self.filter(weather_code__in=[0, 1])

    def above_temperature(self, threshold: float):
        """Возвращает записи, где максимальная температура выше порога.

        Нужен для выборки дней по пользовательскому температурному условию.

        Args:
            threshold (float): Температурный порог для поля `temperature_max`.

        Returns:
            WeatherRecordQuerySet: QuerySet, содержащий записи выше указанного порога.
        """

        return self.filter(temperature_max__gt=threshold)

    def hottest_and_windiest(self):
        """Сортирует записи по максимальной температуре и силе ветра.

        Нужен как базовая выборка для получения топа самых жарких и ветреных
        дней без дублирования сортировки в сервисном слое.

        Returns:
            WeatherRecordQuerySet: QuerySet, отсортированный по убыванию температуры,
                затем по убыванию максимальной скорости ветра и дате.
        """

        return self.order_by('-temperature_max', '-wind_speed_max', '-date')

    def apply_filters(self, filters: dict):
        """Применяет динамический набор фильтров к queryset.

        Нужен для endpoint'а сложного поиска, где пользователь может передать
        только часть параметров, а система должна гибко собрать итоговый запрос.

        Args:
            filters (dict): Словарь с динамическими параметрами фильтрации и сортировки.
                Может содержать следующие поля:
                - start_date (date | None): Нижняя граница диапазона дат. Если передана,
                  в выборку попадут записи с датой не раньше указанной.
                - end_date (date | None): Верхняя граница диапазона дат. Если передана,
                  в выборку попадут записи с датой не позже указанной.
                - max_temperature_from (float | None): Нижняя граница для дневной
                  максимальной температуры `temperature_max`.
                - max_temperature_to (float | None): Верхняя граница для дневной
                  максимальной температуры `temperature_max`.
                - min_temperature_from (float | None): Нижняя граница для дневной
                  минимальной температуры `temperature_min`.
                - min_temperature_to (float | None): Верхняя граница для дневной
                  минимальной температуры `temperature_min`.
                - max_apparent_temperature_from (float | None): Нижняя граница для
                  максимальной ощущаемой температуры `apparent_temperature_max`.
                - max_apparent_temperature_to (float | None): Верхняя граница для
                  максимальной ощущаемой температуры `apparent_temperature_max`.
                - min_apparent_temperature_from (float | None): Нижняя граница для
                  минимальной ощущаемой температуры `apparent_temperature_min`.
                - min_apparent_temperature_to (float | None): Верхняя граница для
                  минимальной ощущаемой температуры `apparent_temperature_min`.
                - wind_speed_max_from (float | None): Нижняя граница для максимальной
                  скорости ветра за день `wind_speed_max`.
                - wind_speed_max_to (float | None): Верхняя граница для максимальной
                  скорости ветра за день `wind_speed_max`.
                - latitude_from (float | None): Нижняя граница диапазона широты `latitude`.
                - latitude_to (float | None): Верхняя граница диапазона широты `latitude`.
                - longitude_from (float | None): Нижняя граница диапазона долготы `longitude`.
                - longitude_to (float | None): Верхняя граница диапазона долготы `longitude`.
                - weather_codes (list[int] | None): Список допустимых кодов погоды. Если
                  передан, в выборку попадут только записи, у которых `weather_code`
                  входит в этот список.
                - ordering (str | None): Поле и направление сортировки результата.

        Returns:
            WeatherRecordQuerySet: QuerySet, к которому применены все переданные фильтры.
        """

        queryset = self

        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        max_temperature_from = filters.get('max_temperature_from')
        max_temperature_to = filters.get('max_temperature_to')
        min_temperature_from = filters.get('min_temperature_from')
        min_temperature_to = filters.get('min_temperature_to')
        max_apparent_temperature_from = filters.get('max_apparent_temperature_from')
        max_apparent_temperature_to = filters.get('max_apparent_temperature_to')
        min_apparent_temperature_from = filters.get('min_apparent_temperature_from')
        min_apparent_temperature_to = filters.get('min_apparent_temperature_to')
        wind_speed_max_from = filters.get('wind_speed_max_from')
        wind_speed_max_to = filters.get('wind_speed_max_to')
        latitude_from = filters.get('latitude_from')
        latitude_to = filters.get('latitude_to')
        longitude_from = filters.get('longitude_from')
        longitude_to = filters.get('longitude_to')
        weather_codes = filters.get('weather_codes')

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if max_temperature_from is not None:
            queryset = queryset.filter(temperature_max__gte=max_temperature_from)
        if max_temperature_to is not None:
            queryset = queryset.filter(temperature_max__lte=max_temperature_to)
        if min_temperature_from is not None:
            queryset = queryset.filter(temperature_min__gte=min_temperature_from)
        if min_temperature_to is not None:
            queryset = queryset.filter(temperature_min__lte=min_temperature_to)
        if max_apparent_temperature_from is not None:
            queryset = queryset.filter(apparent_temperature_max__gte=max_apparent_temperature_from)
        if max_apparent_temperature_to is not None:
            queryset = queryset.filter(apparent_temperature_max__lte=max_apparent_temperature_to)
        if min_apparent_temperature_from is not None:
            queryset = queryset.filter(apparent_temperature_min__gte=min_apparent_temperature_from)
        if min_apparent_temperature_to is not None:
            queryset = queryset.filter(apparent_temperature_min__lte=min_apparent_temperature_to)
        if wind_speed_max_from is not None:
            queryset = queryset.filter(wind_speed_max__gte=wind_speed_max_from)
        if wind_speed_max_to is not None:
            queryset = queryset.filter(wind_speed_max__lte=wind_speed_max_to)
        if latitude_from is not None:
            queryset = queryset.filter(latitude__gte=latitude_from)
        if latitude_to is not None:
            queryset = queryset.filter(latitude__lte=latitude_to)
        if longitude_from is not None:
            queryset = queryset.filter(longitude__gte=longitude_from)
        if longitude_to is not None:
            queryset = queryset.filter(longitude__lte=longitude_to)
        if weather_codes:
            queryset = queryset.filter(weather_code__in=weather_codes)

        ordering = filters.get('ordering', '-date')
        return queryset.order_by(ordering)
