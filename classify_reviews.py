import os
import csv
import json
import time
import requests

if os.path.exists(".env"):
    for line in open(".env"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k, v)

api_key = os.environ.get("OPENROUTER_API_KEY")
model = "openai/gpt-4o-mini"
url = "https://openrouter.ai/api/v1/chat/completions"

input_file = "data/input_reviews.csv"
output_file = "results.json"

prompt = """Ты классификатор отзывов. Определи тональность и тему отзыва.
Ответь ТОЛЬКО JSON-объектом без лишнего текста:
{{"sentiment": "positive" | "negative" | "neutral", "topic": "<тема в 1-3 слова>", "confidence": <число от 0 до 1>}}

Заголовок: {title}
Текст: {content}"""


def classify(title, content):
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt.format(title=title, content=content)}],
        "temperature": 0,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    r = requests.post(url, headers=headers, json=body, timeout=60)
    r.raise_for_status()
    text = r.json()["choices"][0]["message"]["content"]
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end])


def main():
    if not api_key:
        raise SystemExit("Не задан OPENROUTER_API_KEY (см. .env.example)")

    with open(input_file, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    results = []
    correct = 0
    for row in rows:
        ans = classify(row["title"], row["content"])
        ok = ans.get("sentiment") == row["true_label"]
        correct += ok
        results.append({
            "id": int(row["id"]),
            "title": row["title"],
            "predicted_sentiment": ans.get("sentiment"),
            "topic": ans.get("topic"),
            "confidence": ans.get("confidence"),
            "true_label": row["true_label"],
            "correct": ok,
        })
        mark = "ok" if ok else f"wrong (true={row['true_label']})"
        print(f"{row['id']}/{len(rows)} -> {ans.get('sentiment')} | {ans.get('topic')} | {mark}")
        time.sleep(0.3)

    summary = {
        "model": model,
        "total": len(rows),
        "correct": correct,
        "accuracy": round(correct / len(rows), 3),
        "results": results,
    }
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\nТочность: {correct}/{len(rows)} = {summary['accuracy']}")
    print(f"Результат сохранён в {output_file}")


if __name__ == "__main__":
    main()
