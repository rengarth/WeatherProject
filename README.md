# Weather Service API

## Быстрый старт

### Запуск всего проекта через Docker Compose

1. Убедиться, что Docker и Docker Compose доступны на машине.
2. Скопировать `.env.example` в `.env` и при необходимости изменить значения переменных.
3. Выполнить команду:

```bash
docker compose up --build
```

После запуска будут доступны:

- Swagger UI: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- PostgreSQL на хосте: `localhost:5434`


## 1. Общее описание проекта и стека

Проект представляет собой Django REST API для загрузки исторических погодных данных из Open-Meteo, сохранения этих данных в PostgreSQL и последующего анализа через набор HTTP-endpoint'ов.

Основной стек:

- Python 3.14
- Django 6
- Django REST Framework
- drf-spectacular для OpenAPI/Swagger
- PostgreSQL
- Docker и Docker Compose
- requests, requests-cache, retry-requests для работы с внешним API

Проект организован по слоям:

- `WeatherApp/models.py` — ORM-модель погодной записи
- `WeatherApp/querysets.py` — переиспользуемые ORM-запросы и динамические фильтры
- `WeatherApp/serializers.py` — request/response DTO и валидация входных данных
- `WeatherApp/clients.py` — клиент для обращения к Open-Meteo
- `WeatherApp/services.py` — бизнес-логика приложения
- `WeatherApp/views.py` — HTTP-слой и endpoint'ы
- `WeatherApp/exception_handlers.py` и `WeatherApp/exceptions.py` — централизованная обработка ошибок
- `sql/ddl.sql` — DDL-скрипт по условию тестового задания


## 2. Список эндпоинтов

Служебные endpoint'ы:

- `GET /api/docs/` — Swagger UI
- `GET /api/schema/` — OpenAPI schema
- `GET /admin/` — Django admin

Погодные endpoint'ы:

- `POST /api/v1/weather/load/`
  Загружает данные из Open-Meteo за указанный диапазон дат и сохраняет их в БД.

- `GET /api/v1/weather/records/`
  Возвращает полный список сохранённых погодных записей.

- `DELETE /api/v1/weather/records/`
  Удаляет все погодные записи из базы данных.

- `GET /api/v1/weather/records/sunny/`
  Возвращает только солнечные дни, где `weather_code` равен `0` или `1`.

- `GET /api/v1/weather/records/sunny/count/`
  Возвращает количество солнечных дней.

- `GET /api/v1/weather/records/temperature-above/?threshold=<value>`
  Возвращает дни, где `temperature_max` больше переданного порога.

- `GET /api/v1/weather/records/temperature-above/count/?threshold=<value>`
  Возвращает количество дней, где `temperature_max` больше переданного порога.

- `GET /api/v1/weather/records/top-extreme/`
  Возвращает 3 дня, отсортированные по максимальной температуре и затем по максимальной скорости ветра.

- `POST /api/v1/weather/records/filter/`
  Возвращает записи по динамическому набору фильтров. В ответе приходит:
  - `count` — количество найденных записей
  - `records` — список записей

Пример запроса для загрузки данных:

```json
{
  "latitude": 55.7558,
  "longitude": 37.6176,
  "start_date": "2026-01-20",
  "end_date": "2026-03-20"
}
```

Пример запроса для динамической фильтрации:

```json
{
  "start_date": "2026-01-20",
  "end_date": "2026-03-20",
  "max_temperature_from": 15,
  "max_temperature_to": 30,
  "wind_speed_max_from": 2,
  "wind_speed_max_to": 12,
  "latitude_from": 55.0,
  "latitude_to": 56.0,
  "longitude_from": 37.0,
  "longitude_to": 38.0,
  "weather_codes": [0, 1],
  "ordering": "-date"
}
```

## 3. Используемые модели

В проекте используется одна основная модель: `WeatherRecord`.

Поля модели:

- `date` — дата погодной записи
- `latitude` — широта
- `longitude` — долгота
- `temperature_max` — максимальная температура за день
- `temperature_min` — минимальная температура за день
- `apparent_temperature_max` — максимальная ощущаемая температура
- `apparent_temperature_min` — минимальная ощущаемая температура
- `weather_code` — код погодного состояния
- `wind_speed_max` — максимальная скорость ветра за день
- `created_at` — дата и время создания записи
- `updated_at` — дата и время последнего обновления записи

Ограничения модели:

- для одной и той же комбинации `date + latitude + longitude` в таблице может существовать только одна запись
- это обеспечивается ограничением `unique_weather_record_per_date_and_location`

Загрузка данных работает как `upsert`: если запись за эту дату и эти координаты уже существует, она обновляется; если нет, создаётся новая.

## 4. Описание `clients.py`

Файл `WeatherApp/clients.py` отвечает за обращение к Open-Meteo Archive API:

- используется URL `https://archive-api.open-meteo.com/v1/archive`
- запрашиваются именно дневные показатели
- из внешнего API берутся следующие поля:
  - `temperature_2m_max`
  - `temperature_2m_min`
  - `apparent_temperature_max`
  - `apparent_temperature_min`
  - `weather_code`
  - `wind_speed_10m_max`

Почему создаётся session:

- session позволяет централизованно задать поведение HTTP-клиента
- настройки retry и cache определяются один раз при инициализации клиента
- это делает клиент устойчивее и чище архитектурно, чем разрозненные `requests.get(...)` без общей конфигурации

Почему добавлен retry:

- временные сетевые сбои или короткие ошибки внешнего API не должны сразу ломать сценарий загрузки
- используется `retry-requests`
- настроено `5` повторных попыток
- используется `backoff_factor = 0.2`

Почему добавлено кэширование:

- исторические данные запрашиваются повторно довольно часто, особенно при тестировании
- нет смысла каждый раз заново обращаться к внешнему API за одинаковыми архивными данными
- используется `requests-cache`
- кэш хранится локально в `.cache/openmeteo_cache`
- для архивных данных установлен `expire_after = -1`, то есть без автоматического истечения срока

Что проверяет клиент дополнительно:

- успешность HTTP-ответа
- корректность JSON
- наличие блока `daily` в ответе Open-Meteo

Если что-то идёт не так, клиент выбрасывает доменные исключения:

- `ExternalApiError`
- `WeatherDataValidationError`

## 5. Описание сервисного слоя

Файл `WeatherApp/services.py` — это центральный слой бизнес-логики приложения.

Сервисный слой:

- получает данные от клиента Open-Meteo
- валидирует согласованность массивов в ответе
- сохраняет данные в базу
- считает, сколько записей было создано и сколько обновлено
- отдаёт ORM-данные для endpoint'ов аналитики
- выполняет очистку таблицы

Основные методы сервиса:

- `load_weather_data(...)`
  Основной сценарий загрузки данных из внешнего API в базу.
  Выполняет `update_or_create(...)` по ключу `date + latitude + longitude`.
  Возвращает:
  - `created_records_count`
  - `updated_records_count`
  - `total_records_processed`

- `get_all_records()`
  Возвращает все погодные записи.

- `get_sunny_days()`
  Возвращает только солнечные дни.

- `get_sunny_days_count()`
  Возвращает количество солнечных дней.

- `get_days_above_temperature(threshold)`
  Возвращает записи с `temperature_max > threshold`.

- `get_days_above_temperature_count(threshold)`
  Возвращает количество записей с `temperature_max > threshold`.

- `get_top_3_hottest_and_windiest_days()`
  Возвращает 3 записи, отсортированные по максимальной температуре и скорости ветра.

- `filter_records(filters)`
  Делегирует сложную фильтрацию в `WeatherRecordQuerySet.apply_filters(...)`.

- `clear_all_records()`
  Полностью очищает таблицу погодных записей.


## Дополнительно

SQL DDL-скрипт находится в файле:

- [sql/ddl.sql](sql/ddl.sql)

Основные Docker-файлы:

- [Dockerfile](Dockerfile)
- [docker-compose.yml](docker-compose.yml)
- [entrypoint.sh](entrypoint.sh)
