## my_account

Telegram‑бот для мониторинга аккаунта на бирже Gate.io: баланс кошелька, P2P‑ордера и новости о делистинге. Работает по расписанию и по командам пользователя.

---

### Возможности

- **Баланс кошелька**
  - Периодически запрашивает общий баланс через локальный сервис `gate_rest_api` (`/wallet/total_balance`).
  - Команда `/balance` — отправляет таблицу с суммарным балансом и деталями по валютам.
- **P2P‑рынок**
  - Команда вида `P2P покупка RUB-USDT` или `P2P продажа USDT-RUB` — парсит HTML‑страницу P2P Gate.io через Selenium и отправляет список актуальных ордеров.
  - Кэширует последний результат, чтобы не дублировать одинаковые уведомления.
- **Делистинг и объявления**
  - Периодическая задача `action_2` — парсит страницу анонсов/делистинга (`URL_PATH_ANNONCE`) и присылает новые новости.
- **Управление ботом**
  - `/add_buttons` — добавить клавиатуру с основными командами.
  - `/del_buttons` — убрать клавиатуру.
  - `/logs` — отправить текущий лог‑файл бота.
  - `/help` — список доступных команд с описанием.
  - `/check`, `/pause`, `/active`, `/stop` — служебные команды (проверка, пауза, возобновление, остановка).

Все команды доступны только владельцу (чат ID из переменных окружения) или при совпадении `CONTAINER_ID`.

---

### Технологии

- **Python 3.12**
- **pyTelegramBotAPI** (асинхронный `AsyncTeleBot`)
- **Selenium** (удалённый WebDriver, переменная `CHROME_IP_ADDRESS`/`FIREFOX_DOMAIN`)
- **aiohttp**, **BeautifulSoup4** — для HTTP‑запросов и парсинга HTML
- **gate-api** — официальная библиотека Gate.io
- **APScheduler** — планировщик периодических задач
- Логирование в файл `./log/<CONTAINER_ID>_my_account.log` (ротация по размеру)

---

### Переменные окружения

Основные переменные задаются через `.env` и файлы в `env/`:

- **Telegram**
  - `TELEGRAM_HOST` — хост API Telegram (`https://api.telegram.org` по умолчанию)
  - `TELEGRAM_BOT_TOKEN` — токен бота
  - `TELEGRAM_CHAT_ID` — ID чата владельца (доступ к командам)
  - `TELEGRAM_CONN_TIME` — таймаут подключения
- **Gate.io (прямой доступ и/или через gate_rest_api)**
  - `GATE_HOST` — базовый URL API Gate.io
  - `GATE_KEY`, `GATE_SECRET` — API‑ключ и секрет
  - `LOCAL_GATE_REST_API_IP`, `LOCAL_GATE_REST_API_PORT` — адрес локального сервиса `gate_rest_api`
- **Расписание**
  - `BOT_SCHED_INTERVAL` — период задачи `action` (баланс), минуты
  - `BOT_SCHED_INTERVAL_2` — период задачи `action_2` (делистинг), минуты
- **Контейнер / прочее**
  - `CONTAINER_ID` — ID контейнера/инстанса (используется в логах и проверке доступа)
  - `BOT_NAME` — имя бота (по умолчанию `my_account`)
  - `CHROME_IP_ADDRESS` / `FIREFOX_DOMAIN` — адрес удалённого Selenium WebDriver

Точный список можно посмотреть в `app/config.py` и `docker-compose.yml`.

---

### Установка и запуск (локально)

```bash
cd my_account
pip install -r requirements.txt

# заполнить .env или env/* значениями Telegram, Gate.io и gate_rest_api

python -m app
```

При запуске:

- создаются директории `./app/log` и `./app/data` (если отсутствуют);
- настраивается планировщик `APScheduler` с задачами `action` и `action_2`;
- запускается асинхронный polling Telegram‑бота.

---

### Запуск в Docker

```bash
cd my_account
docker compose up -d
```

`docker-compose.yml`:

- строит образ из `Dockerfile`;
- монтирует внешний volume `gate_io_log` в `/usr/src/app/log`;
- подхватывает переменные из:
  - `env/variable.env`
  - `env/<BRANCH>/gate.env`
  - `env/<BRANCH>/telegram.env`
  - `env/<BRANCH>/database.env`

---

### Структура

```text
my_account/
├── app/
│   ├── __main__.py          # точка входа, scheduler + polling
│   ├── config.py            # конфигурация, TELEGRAM_*, GATE_*, интервалы
│   ├── runners.py           # фоновые задачи: баланс, делистинг, P2P
│   ├── telebot_handler.py   # обработчики команд и сообщений
│   ├── util.py, global_obj.py, literals.py
│   └── gate_wrapper/        # обёртка над gate-api, парсеры ответов
├── docker-compose.yml
├── Dockerfile
├── requirements.in / requirements.txt
└── env/                     # переменные окружения для разных окружений
```

---

### Команды бота (кратко)

- `/add_buttons` — добавить клавиатуру.
- `/del_buttons` — удалить клавиатуру.
- `/balance` — показать баланс кошелька на Gate.io.
- `/logs` — получить лог‑файл.
- `/check_delisted_info` — проверить новости о делистинге.
- `P2P покупка RUB-USDT` / `P2P продажа USDT-RUB` — показать P2P‑ордера.
- `/check`, `/pause`, `/active`, `/stop`, `/help` — служебные и информационные команды.
