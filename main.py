import os
import threading
from queue import Queue
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

def process_request(question, request_queue):
    # Create unique logger for this request
    logger = RequestLogger()
    request_id = logger.generate_request_id()
    request_logger = logger.create_request_log(request_id)
    
    request_logger.info(f"STARTING REQUEST {request_id}")
    request_logger.info(f"USER INPUT: {question}")
    
    try:
        prompt = load_prompt().format(question=question)
        
        client = OpenAI(api_key=os.getenv("API_KEY"), base_url="https://api.deepseek.com")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Sie sind ein professioneller akademischer Schreibassistent, der dabei hilft, Texte in eine formelle, wissenschaftliche Sprache zu übertragen. Sie unterstützen bei der Verbesserung von Struktur, Stil und Präzision gemäß akademischer Standards. Ihre Korrekturen umfassen Grammatik, Syntax, Kohärenz und korrekte Zitierweise. Gehen Sie auf spezifische Anforderungen ein und bieten Sie konstruktive Verbesserungsvorschläge an."},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
        
        response_text = response.choices[0].message.content
        request_logger.info(f"AI RESPONSE:\n{response_text}")
        
        # Put the result in the queue
        request_queue.put((question, response_text))
        
    except Exception as e:
        error_msg = f"ERROR: {str(e)}"
        request_logger.error(error_msg)
        request_queue.put((question, f"Error: {error_msg}"))
    finally:
        request_logger.info(f"COMPLETED REQUEST {request_id}\n")

def main():
    request_queue = Queue()
    active_threads = []
    
    while True:
        question = input("\nWhat do you want me to do? (Type 'exit' to quit or 'status' to check threads)\n")
        
        if question.lower() == 'exit':
            # Wait for all threads to complete before exiting
            for thread in active_threads:
                thread.join()
            print("Exiting...")
            break
            
        if question.lower() == 'status':
            print(f"\nActive threads: {threading.active_count() - 1}")  # Subtract 1 for main thread
            continue
            
        # Start a new thread for each request
        thread = threading.Thread(
            target=process_request,
            args=(question, request_queue),
            daemon=True
        )
        thread.start()
        active_threads.append(thread)
        
        # Clean up finished threads
        active_threads = [t for t in active_threads if t.is_alive()]
        
        # Check for completed requests
        while not request_queue.empty():
            question, response = request_queue.get()
            print(f"\nResponse for '{question[:30]}...':\n{response}")

if __name__ == "__main__":
    main()
