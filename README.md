# Задание 2 - классификация отзывов через LLM API

Скрипт читает отзывы из CSV, отправляет каждый в LLM через API (OpenRouter), получает
ответ в формате JSON (тональность + тема) и сохраняет всё в файл `results.json`.

## Что делает скрипт

1. Читает отзывы из `data/input_reviews.csv`.
2. Для каждого отзыва отправляет запрос в модель через OpenRouter.
3. Модель возвращает JSON: `sentiment`, `topic`, `confidence`.
4. Скрипт собирает все ответы, считает точность (сравнивает с реальной меткой) и
   сохраняет результат в `results.json`.

## Как запустить

1. Установить зависимость:
   ```
   pip install -r requirements.txt
   ```
2. Создать файл `.env` (по образцу `.env.example`) и вписать свой ключ OpenRouter:
   ```
   OPENROUTER_API_KEY=sk-or-...
   ```
   Модель задаётся прямо в коде (`classify_reviews.py`, переменная `model`),
   по умолчанию `openai/gpt-4o-mini`.
3. Запустить:
   ```
   python classify_reviews.py
   ```

## Пример входных данных (`data/input_reviews.csv`)

```
id,title,content,true_label
1,Great album,"One of the best albums I have ever bought...",positive
```

## Пример результата (`results.json`)

```json
{
  "model": "openai/gpt-4o-mini",
  "total": 30,
  "correct": 29,
  "accuracy": 0.967,
  "results": [
    {
      "id": 1,
      "title": "Great album",
      "predicted_sentiment": "positive",
      "topic": "music",
      "confidence": 0.98,
      "true_label": "positive",
      "correct": true
    }
  ]
}
```
