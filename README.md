# \[Trader\] Finam x HSE Trade AI Hack - Baseline

> **AI-ассистент трейдера** на базе Finam TradeAPI
> Базовый шаблон для хакатона по созданию интеллектуального помощника для трейдинга

## ✨ Новое: LangGraph Agent System

Реализована агентная система на базе LangGraph с двумя специализированными агентами:

- **Route Agent** - координирует задачи и делегирует их специализированным агентам
- **API Agent** - работает с Finam API, ищет активы и получает рыночные данные

### Быстрый старт с агентами

```bash
# Использование CLI
agent-cli "Найди информацию об акциях Газпром"

# Запуск демо
python examples/demo_agents.py

# Python API
from src.app.agents import run_agent_workflow
result = run_agent_workflow("Найди акции Сбербанк")
```

📖 **Документация:** [docs/agents.md](docs/agents.md) | [docs/agent_usage.md](docs/agent_usage.md)

## 🚀 Быстрый старт

### Вариант 1: Docker (рекомендуется)

```bash
# 1. Скопируйте пример конфигурации
cp .env.example .env

# 2. Отредактируйте .env и добавьте API ключи
# OPENROUTER_API_KEY=your_key
# FINAM_ACCESS_TOKEN=your_token (опционально)

# 3. Запустите приложение
make up
# или: docker-compose up -d

# 4. Откройте в браузере
# http://localhost:8501
```

### Вариант 2: Локально

```bash
# 1. Установите зависимости
poetry install

# 2. Настройте .env
cp .env.example .env

# 3. Запустите веб-интерфейс
poetry run streamlit run src/app/interfaces/chat_app.py

# ИЛИ CLI чат
poetry run chat-cli

# ИЛИ агентная система
poetry run agent-cli "Найди акции Газпром"
```

## 📋 Основные команды

```bash
# Генерация submission.csv
make generate
# или: poetry run generate-submission

# Валидация submission
make validate
# или: poetry run validate-submission

# Подсчет метрики
make metrics
# или: poetry run calculate-metrics

# Агентная система
poetry run agent-cli "Найди акции Газпром"
python examples/demo_agents.py

# Тесты
pytest tests/test_agents.py -v

# Просмотр логов Docker
```

## 🎯 Задача

Создать AI-ассистента, который преобразует вопросы на естественном языке в HTTP запросы к Finam TradeAPI.

**Пример:**
- Вопрос: *"Какая цена Сбербанка?"*
- API запрос: `GET /v1/instruments/SBER@MISX/quotes/latest`

**Метрика:**
```
Accuracy = N_correct / N_total
```

Запрос считается правильным, если полностью совпал с эталоном (и HTTP метод, и путь).

## 📁 Структура проекта

```
├── src/app/
│   ├── adapters/          # Finam API клиент
│   ├── agents/            # LangGraph агентная система
│   │   ├── tools.py       # Инструменты (search_asset, get_quote, etc.)
│   │   ├── api_agent.py   # API агент
│   │   ├── route_agent.py # Route агент (координатор)
│   │   ├── graph.py       # LangGraph workflow
│   │   └── state.py       # State management
│   ├── core/              # Основная логика (LLM, config)
│   └── interfaces/        # UI (Streamlit, CLI, Agent CLI)
├── examples/              # Примеры использования
│   └── demo_agents.py     # Демо агентной системы
├── scripts/               # Утилиты
│   ├── generate_submission.py
│   ├── validate_submission.py
│   └── calculate_metrics.py
├── data/processed/
│   ├── train.csv         # 100 обучающих примеров
│   ├── test.csv          # 300 тестовых вопросов
│   └── submission.csv    # Ваши предсказания
├── docs/                 # Документация хакатона
│   ├── agents.md         # Документация агентной системы
│   └── agent_usage.md    # Руководство по использованию
└── tests/                # Тесты
    └── test_agents.py    # Тесты агентной системы
```

## 🔑 Необходимые API ключи

1. **OpenRouter API** (обязательно)
   - Регистрация: https://openrouter.ai/
   - Используется для LLM (GPT-4o-mini, GPT-4o, Claude и др.)

2. **Finam TradeAPI** (опционально для чата)
   - Документация: https://tradeapi.finam.ru/
   - Нужен только для работы с реальным API в чат-интерфейсе

## 💡 Что дальше?

### Для участников хакатона:
1. **Улучшите accuracy** - экспериментируйте с промптами, few-shot примерами, моделями
2. **Реализуйте продвинутые кейсы** - портфельный анализ, визуализация, бэктестинг
3. **Создайте UI** - используйте готовый Streamlit или создайте свой

### Полезные ссылки:
- [DEVELOPMENT.md](DEVELOPMENT.md) - подробная информация для разработки
- [SUMMARY.md](SUMMARY.md) - итоговое резюме проекта
- [docs/task.md](docs/task.md) - полное описание задачи
- [docs/evaluation.md](docs/evaluation.md) - методология оценки

## 📊 Пример работы

**Генерация submission:**
```bash
poetry run generate-submission --num-examples 15

🚀 Генерация submission файла...
✅ Загружено 15 примеров для few-shot learning
🤖 Используется модель: openai/gpt-4o-mini

Обработка: 100%|████████| 300/300 [02:15, cost=$0.0423]

💰 Общая стоимость: $0.0423
📊 GET: 285, POST: 12, DELETE: 3
```

**Подсчет метрики:**
```bash
poetry run calculate-metrics

🎯 ОСНОВНАЯ МЕТРИКА:
   Accuracy = 87/100 = 0.8700 (87.00%)
```

## 🤝 Поддержка

Для вопросов по хакатону обращайтесь к организаторам.

## 📄 Лицензия

Этот проект создан как baseline для хакатона Finam x HSE.
