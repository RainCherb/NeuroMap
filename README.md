# NeuroMap — ИИ-оптимизированные карты проектов для понимания крупных кодовых баз

[![Build](https://img.shields.io/github/actions/workflow/status/neuromap-ai/neuromap/test.yml)](https://github.com/neuromap-ai/neuromap/actions)
[![Python](https://img.shields.io/pypi/pyversions/neuro-map.svg)](https://pypi.org/project/neuro-map)
[![License](https://img.shields.io/github/license/neuromap-ai/neuromap.svg)](https://github.com/neuromap-ai/neuromap/blob/main/LICENSE)

## О проекте

Когда кодовая база становится очень большой и в ней много файлов, ИИ-модели начинают тупить и путаться. **NeuroMap** создает подробную карту проекта, которую легко прочитает нейросеть даже с небольшим количеством контекста.

Он разжёвывает для нейросети всё так, чтобы она начала понимать суть и структуру проекта.

## Установка

```bash
pip install neuromap
```

Или с dev-зависимостями:

```bash
pip install neuromap[dev]
```

## Быстрый старт

### Создание карты

```bash
# Быстрая компактная карта (~500 токенов)
neuromap scan ./my-project

# Стандартная карта с лимитом токенов
neuromap scan ./my-project --level standard --max-tokens 2000

# Полная детальная карта в JSON
neuromap scan ./my-project --level detailed --format json -o ai_context.json
```

### Примеры использования

#### 1. Компактная карта для общего понимания

```bash
neuromap scan ./my-project --level compact --format markdown
```

Вывод (пример):
```markdown
# my-project

**Языки:** Python 3.11
**Всего файлов:** 42
**Кодовых строк:** 1578
**Каталогов:** 7

## Entry Points
- `src/main.py`: Основная точка входа приложения
- `src/api/router.py`: REST API роутер

## Key Symbols
- `Engine.process` в engine.py (function)
- `UserModel` в models.py (class)
```

#### 2. Стандартная карта для разработки

```bash
neuromap scan ./my-project --level standard --format json > project_context.json
```

#### 3. Детальная карта для знакомства с архитектурой

```bash
neuromap scan ./my-project --level detailed --format markdown --output PROJECT_MAP.md
```

Вывод содержит:
- Полный файл с деревом с аннотациями
- Индекс всех символов с сигнатурами
- Визуализацию зависимостей
- Архитектурный анализ

## Форматы вывода

### Markdown
Идеально читается людьми и ИИ. Содержит структурированную информацию о проекте.

### JSON
Машиночитаемый формат, идеально подходит для построения инструментов на основе NeuroMap.

### XML
Стандартизированный формат для системных промптов и интеграции с другими инструментами.

## Настройка

### Конфигурационный файл

Создайте `.neuromap/config.json`:

```json
{
  "default_level": "compact",
  "default_max_tokens": 1000,
  "default_format": "markdown",
  "exclude_patterns": ["*.test.*", "__pycache__", ".git"],
  "include_patterns": [],
  "entrypoints": {
    "detect_main": true,
    "detect_api": true,
    "detect_cli": true,
    "detect_worker": true
  }
}
```

### Пользовательский конфиг через CLI

```bash
neuromap config set default_level standard
neuromap config set default_max_tokens 2000
```

## Поддерживаемые языки

- **Python** (3.11+)
- **JavaScript / TypeScript** (ES6+)
- **Java** (8+)
- **C / C++**
- **Rust**
- **Go**
- **PHP**
- **Ruby**
- **Swift**
- **Kotlin**

## Архитектурные детекторы

### Entry Points
- **Main** — Основная точка входа (`main()`)
- **API** — REST API эндпоинты (FastAPI, Django, Spring)
- **CLI** — Командная строка (Click, Typer)
- **Worker** — Фоновые задачи (Celery, Daphne)

### Фреймворки
- **FastAPI** — Современные API
- **Django** / **DRF** — Классические веб-фреймворки
- **Spring** — Java экосистема
- **React** — Фронтенд (через JSX парсеры)

### Паттерны
- **MVC** — Модель-Представление-Контроллер
- **Clean Architecture** — Слои ответственности
- **Microservices** — Визуализация сервисов
- **Monolithic** — Единая структура приложения

## Технологии

- **Typer** — Современный CLI фреймворк
- **Rich** — Красивый терминал вывод
- **Tree-sitter** — Парсинг кода (интеграция в процессе)
- **NetworkX** — Граф зависимостей
- **Tiktoken** — Подсчёт токенов
- **Pydantic** — Валидация данных

## Бэкенд нейронных сетей (будущие планы)

NeuroMap может быть расширен следующими модулями:

1. **Графовые нейронные сети** — Анализ архитектуры
2. **Code2Query** — Генерация запросов к ИИ
3. **PatternLearner** — Обучение на архитектурных шаблонах
4. **ImpactAnalyzer** — Анализ влияния изменений

## Лицензия

MIT

## КОНТРИБУЦИИ

Мы приветствуем вклады в проект! Пожалуйста, ознакомьтесь с [инструкциями по вкладу](./CONTRIBUTING.md) перед отправкой pull request.

## Связь

- Discord: [neuromap.ai/discord](https://neuromap.ai/discord)
- Twitter: [@neuromap_ai](https://twitter.com/neuromap_ai)
- GitHub: [neuromap-ai/neuromap](https://github.com/neuromap-ai/neuromap)

## Примечания

В этом проекте используется:
- `tree-sitter` для парсинга кода (будет добавлено в следующей версии)
- `NetworkX` для построения графа зависимостей
- `Tiktoken` для точного подсчёта токенов
- `Pydantic` для валидации конфигурации
