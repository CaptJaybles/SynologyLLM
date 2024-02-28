from flask import Flask, request
import json
import os
import time
import psutil
import requests
import threading
import queue
from synology import OutgoingWebhook
from settings import *
from llama_cpp import Llama

app = Flask(__name__)
llm = None
user_data = {}
task_queue = queue.Queue()
queue_lock=threading.Semaphore(value=1)

def initialize_llm():
    global llm
    llm = Llama(model_path=f"./model/{MODEL_FILENAME}", n_threads=N_THREADS, n_ctx=N_CTX, n_gpu_layers=N_GPU_LAYERS, lora_base=LORA_BASE, lora_path=LORA_PATH, rope_freq_base=ROPE_FREQ_BASE, rope_freq_scale=ROPE_FREQ_SCALE)
    warmup_input = "Human: Name the planets in the solar system? Assistant:"
    llm(warmup_input, max_tokens=64, stop=["Human:", "\n"], echo=False)
    llm.reset()
    print("LLM Loaded")

def check_memory():
    global llm
    enable = MEMORY_CHECKER
    while True:
        if enable:
            memory_usage = psutil.virtual_memory().percent
            if memory_usage > HIGH_MEMORY and model is not None:
                llm = None
                print("llm suspended due to high memory usage")
            elif memory_usage <= LOW_MEMORY and model is None:
                initialize_llm()
                print("llm resumed")
        time.sleep(1)  # Check memory every second

def send_back_message(user_id, output_text):
    chunks = []
    current_chunk = ""
    sentences = output_text.split("\n\n")
    for sentence in sentences:
        chunks.append(current_chunk.strip())
        current_chunk = sentence + "\n\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
    for chunk in chunks:
        payload = 'payload=' + json.dumps({
            'text': chunk,
            "user_ids": [int(user_id)]
        })
        try:
            response = requests.post(INCOMING_WEBHOOK_URL, payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return "Error", 500
    return queue_lock.release()

def generate_response(message, user_id, user_context):
    global llm, user_data

    output_text = user_context.get('output_text', '')
    current_topic = user_context.get('current_topic', '')

    if message.startswith("/reset"):
        llm.reset
        user_data[user_id] = {'output_text': '', 'current_topic': None}
        response = "Conversation Reset"
        return send_back_message(user_id, response)

    elif message.startswith("/continue"):
        def generate_message():
            output = llm(output_text, max_tokens=MAX_TOKENS, temperature=TEMPURATURE, top_p=TOP_P, top_k=TOP_K, stop=[], repeat_penalty=1.3, frequency_penalty=0.15, presence_penalty=0.15, echo=False)
            answer = output["choices"][0]["text"]
            if current_topic:
                new_current_topic = current_topic + answer
                user_data[user_id] = {'output_text': output_text + answer, 'current_topic': new_current_topic}
            else:
                user_data[user_id] = {'output_text': output_text + answer, 'current_topic': None}
            send_back_message(user_id, answer)
        threading.Thread(target=generate_message).start()
        return "..."

    elif message.startswith("/override"):
        def generate_message():
            prompt = message.replace("/override", "").strip()
            output = model(prompt, max_tokens=MAX_TOKENS, temperature=TEMPURATURE, top_p=TOP_P, top_k=TOP_K, stop=[], repeat_penalty=1.3, frequency_penalty=0.15, presence_penalty=0.15, echo=False)
            answer = output["choices"][0]["text"]
            user_data[user_id] = {'output_text': answer, 'current_topic': None}
            send_back_message(user_id, answer)
        threading.Thread(target=generate_message).start()
        return "..."

    else:
        if current_topic:
            prompt = f"{SYSTEM_PROMPT}{current_topic}\n\n{USER_PROMPT}{message}{USER_END}{BOT_PROMPT}"
        else:
            prompt = f"{SYSTEM_PROMPT}{USER_PROMPT}{message}{USER_END}{BOT_PROMPT}"
        def generate_message():
            output = llm(prompt, max_tokens=MAX_TOKENS, temperature=TEMPURATURE, top_p=TOP_P, top_k=TOP_K, stop=STOP_WORDS, repeat_penalty=REPEAT_PENALTY, frequency_penalty=FREQUENCY_PENALTY, presence_penalty=PRESENCE_PENALTY, echo=False)
            answer = output["choices"][0]["text"]
            user_data[user_id] = {'output_text': answer, 'current_topic': f"{USER_PROMPT}{message}{USER_END}{BOT_PROMPT}{answer}"}
            return send_back_message(user_id, answer)
        threading.Thread(target=generate_message).start()
        return "..."

@app.route('/SynologyLLM', methods=['POST'])
def chatbot():
    token = SYNOCHAT_TOKEN
    webhook = OutgoingWebhook(request.form, token)
    if not webhook.authenticate(token):
        return webhook.createResponse('Outgoing Webhook authentication failed: Token mismatch.')
    message = webhook.text
    user_id = webhook.user_id
    if user_id not in user_data:
        user_data[user_id] = {'output_text': '', 'current_topic': None}
    task_queue.put((message, user_id, user_data[user_id]))
    return "Task queued for processing"

def process_tasks():
    while True:
        queue_lock.acquire()
        try:
            message, user_id, user_context = task_queue.get()
            generate_response(message, user_id, user_context)
        finally:
            task_queue.task_done()

processing_thread = threading.Thread(target=process_tasks, daemon=True)
processing_thread.start()

if __name__ == '__main__':
    initialize_llm()
    memory_thread = threading.Thread(target=check_memory, daemon=True)
    memory_thread.start()
    app.run('0.0.0.0', port=FLASK_PORT, debug=False, threaded=True)
