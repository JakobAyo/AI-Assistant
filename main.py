import os
from openai import OpenAI
from pathlib import Path
from logging_setup import RequestLogger
from dotenv import load_dotenv

load_dotenv()

def load_prompt():
    prompt_path = Path("prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

logger = RequestLogger()
id = logger.generate_request_id()
logger = logger.create_request_log(id)

while True:
    question = input("What do you want me to do ?\n")
    logger.info(question)
    prompt = load_prompt().format(
        question=question
    )


    client = OpenAI(api_key=os.getenv("API_KEY"), base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "Sie sind ein professioneller akademischer Schreibassistent, der dabei hilft, Texte in eine formelle, wissenschaftliche Sprache zu übertragen. Sie unterstützen bei der Verbesserung von Struktur, Stil und Präzision gemäß akademischer Standards. Ihre Korrekturen umfassen Grammatik, Syntax, Kohärenz und korrekte Zitierweise. Gehen Sie auf spezifische Anforderungen ein und bieten Sie konstruktive Verbesserungsvorschläge an."},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    response = response.choices[0].message.content
    print()
    print(response)
    logger.info(response)
