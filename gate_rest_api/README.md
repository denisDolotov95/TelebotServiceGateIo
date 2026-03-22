# Gate.io REST API (FastAPI)

Локальный REST API сервис для взаимодействия с [Gate.io API v4](https://www.gate.io/docs/developers/apiv4/). Реализован на FastAPI.

## Возможности

- **Spot** — спотовые операции: пары, ордера, счета, тикеры, стакан, свечи, отмена ордеров
- **Wallet** — баланс кошелька
- **Admin** — служебная информация о запросах (хост клиента, заголовки)
- Rate limiting через Redis (FastAPI-Limiter)
- Обработка ошибок Gate.io API
- Логирование в файл `./log/gate_rest_api.log`
- Docker и docker-compose для развёртывания

## Стек

- Python 3.12
- FastAPI, Uvicorn
- [gate-api](https://github.com/gateio/gateapi-python) 4.60.2
- Redis (для лимитов запросов)
- Pydantic

## Требования

- Python 3.12+
- Redis (доступный по `IP_ADDRESS_REDIS` и `REDIS_PORT`)

## Установка

```bash
pip install -r requirements.txt
```

Или из исходных зависимостей:

```bash
pip install -r requirements.in
pip-compile requirements.in  # опционально, для обновления requirements.txt
```

## Конфигурация

Переменные окружения:

| Переменная           | Описание                          |
|----------------------|-----------------------------------|
| `FASTAPI_HOST`       | Хост FastApi                      |
| `FASTAPI_PORT`       | Порт FastApi                      |
| `REDIS_HOST`         | Хост Redis                        |
| `REDIS_PORT`         | Порт Redis                        |
| `GATE_HOST`          | Хост Gate.io API                  |
| `GATE_KEY`           | API ключ Gate.io                  |
| `GATE_SECRET`        | Секрет Gate.io                    |
| `SECRET_KEY`         | Секрет приложения (опционально)   |

Метаданные API (название, описание, теги) задаются в `data/api_metadata.json`.

## Запуск

### Локально

```bash
uvicorn app:app --host 127.0.0.1 --port 80
```

Или через главный модуль (порт из `PORT`, воркеры по числу CPU):

```bash
python app.py
```

### Docker

Сборка и запуск через docker-compose (требуется настроенный `.env` с переменными для контейнера, Redis и сети):

```bash
docker compose up -d
```

Только образ:

```bash
docker build -t gate_rest_api .
docker run --env-file .env -p 3500:3500 gate_rest_api
```

## API

После запуска документация доступна по адресам:

- **Swagger UI:** `http://127.0.0.1:<PORT>/docs`
- **ReDoc:** `http://127.0.0.1:<PORT>/redoc`
- **OpenAPI JSON:** `http://127.0.0.1:<PORT>/openapi.json`

### Spot

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/spot/currency_pair` | Информация о паре |
| POST | `/spot/currency_pairs` | Список пар |
| POST | `/spot/orders` | Список ордеров (open/finished) |
| POST | `/spot/cancel_orders` | Отмена ордеров по паре |
| POST | `/spot/all_open_orders` | Все открытые ордера |
| POST | `/spot/spot_accounts` | Спотовые счета |
| POST | `/spot/spot_account_book` | Книга счетов |
| POST | `/spot/trades` | Сделки по паре |
| POST | `/spot/tickers` | Тикеры по паре |
| POST | `/spot/order_book` | Стакан заявок |
| POST | `/spot/candlesticks` | Свечи (с rate limit) |

В теле запроса для большинства эндпоинтов передаётся объект с учётными данными Gate.io: `key`, `secret`, при необходимости `proxy` (модель `Security` в `model.py`). Для части эндпоинтов используется `Payload` с полями `data` и `security`.

### Wallet

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/wallet/total_balance` | Общий баланс кошелька |

### Admin

| Метод | Путь | Описание |
|-------|------|----------|
| GET  | `/admin/{item_id}` | Информация о клиенте (host, headers, item_id) |

## Разработка и тесты

Тесты лежат в `gate_wrapper/tests/`. Запуск:

```bash
pytest -v
```

В CI (GitLab) тесты выполняются по тегам (см. `.gitlab-ci.yml`).

## Структура проекта

```
├── app.py              # Точка входа FastAPI
├── config.py           # Конфигурация (ProductionConfig)
├── model.py            # Pydantic-модели запросов/ответов API
├── exceptions.py       # Обработчик исключений Gate API
├── views/              # Роуты: spot, wallet, administartion
├── gate_wrapper/       # Обёртка над gate-api (spot, wallet, parse, model)
├── data/
│   └── api_metadata.json
├── requirements.in / requirements.txt
├── Dockerfile
├── docker-compose.yaml
└── .gitlab-ci.yml      # Unit-тесты и пересборка контейнера по тегам
```

## Контакты

- Denis D. — gambit0095.mail@gmail.com