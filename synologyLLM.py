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
model = None
output_text = ""
current_topic = None
last_activity_time = 0  # Variable to track the time of the last activity
task_queue = queue.Queue()
processing_semaphore = threading.Semaphore(value=1)

def initialize_model():
    global model
    model = Llama(model_path=f"./model/{MODEL_FILENAME}", n_ctx=CONTEXT_LENGTH, n_gpu_layers=GPU_LAYERS, lora_base=LORA_BASE, lora_path=LORA_PATH, rope_freq_base=ROPE_FREQ_BASE, rope_freq_scale=ROPE_FREQ_SCALE)
    warmup_input = "Human: Name the planets in the solar system? Assistant:"
    model(warmup_input, max_tokens=64, stop=["Human:", "\n"], echo=False)
    model.reset()
    print("LLM Model Loaded")

def check_memory():
    global model
    enable = MEMORY_CHECKER
    while True:
        if enable:
            memory_usage = psutil.virtual_memory().percent
            if memory_usage > HIGH_MEMORY and model is not None:
                model = None
                print("Model suspended due to high memory usage.")
            elif memory_usage <= LOW_MEMORY and model is None:
                initialize_model()
                print("Model resumed.")
        time.sleep(1)  # Check memory every second

def send_back_message(user_id, output_text):
    response = output_text
    chunks = []
    current_chunk = ""
    sentences = response.split("\n\n")
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 2 <= 256:
            current_chunk += sentence + "\n\n"
        else:
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
        finally:
            processing_semaphore.release()
    return "success"

def reset_conversation():
    global output_text, current_topic, model
    model.reset()
    current_topic = None
    output_text = ""

def generate_response(message, user_id, username):
    global last_activity_time, current_topic
    last_activity_time = time.time()

    if message.startswith("/reset"):
        reset_conversation()
        response = "LLM Model Reset"
        return send_back_message(user_id, response)

    elif message.startswith("/continue"):
        def generate_message(): 
            global output_text, model
            output = model(output_text, max_tokens=MAX_TOKENS, temperature=TEMPURATURE, top_p=TOP_P, top_k=TOP_K, stop=[], repeat_penalty=1.3, frequency_penalty=0.15, presence_penalty=0.15)
            answer = output["choices"][0]["text"]
            output_text = answer
            send_back_message(user_id, answer)
        threading.Thread(target=generate_message).start()
        return "..."

    elif message.startswith("/override"):
        def generate_message(): 
            global output_text, model
            prompt = message.replace("/override", "").strip()
            output = model(prompt, max_tokens=MAX_TOKENS, temperature=TEMPURATURE, top_p=TOP_P, top_k=TOP_K, stop=[], repeat_penalty=1.3, frequency_penalty=0.15, presence_penalty=0.15)
            answer = output["choices"][0]["text"]
            output_text = answer
            send_back_message(user_id, answer)
        threading.Thread(target=generate_message).start()
        return "..."

    else:
        if current_topic:
            prompt = f"{SYSTEM_PROMPT}{current_topic}\n\n{USER_PROMPT}{message}{INPUT_PROMPT}{BOT_PROMPT}"
        else:
            prompt = f"{SYSTEM_PROMPT}{USER_PROMPT}{message}{INPUT_PROMPT}{BOT_PROMPT}"
        def generate_message():
            global output_text, model, current_topic
            output = model(prompt, max_tokens=MAX_TOKENS, temperature=TEMPURATURE, top_p=TOP_P, top_k=TOP_K, stop=STOP_WORDS, repeat_penalty=REPEAT_PENALTY, frequency_penalty=FREQUENCY_PENALTY, presence_penalty=PRESENCE_PENALTY)
            answer = output["choices"][0]["text"]
            output_text = answer
            current_topic = f"{USER_PROMPT}{message}\n\n{BOT_PROMPT}{answer}"
            send_back_message(user_id, answer)
        threading.Thread(target=generate_message).start()
        return "..."

@app.before_request
def check_inactivity():
    global last_activity_time
    enable = INACTIVITY_ENABLE
    if enable:
        if time.time() - last_activity_time > INACTIVITY_TIMEOUT:
            reset_conversation()
            print("Model Reset")

@app.route('/synologyLLM', methods=['POST'])
def chatbot():
    token = SYNOCHAT_TOKEN
    webhook = OutgoingWebhook(request.form, token)
    if not webhook.authenticate(token):
        return webhook.createResponse('Outgoing Webhook authentication failed: Token mismatch.')
    message = webhook.text
    user_id = webhook.user_id
    username = webhook.username
    task_queue.put((message, user_id, username))
    return "Task queued for processing"

def process_tasks():
    while True:
        processing_semaphore.acquire()
        try:
            message, user_id, username = task_queue.get()
            generate_response(message, user_id, username)
        finally:
            task_queue.task_done()

if __name__ == '__main__':
    initialize_model()
    memory_thread = threading.Thread(target=check_memory, daemon=True)
    memory_thread.start()
    processing_thread = threading.Thread(target=process_tasks, daemon=True)
    processing_thread.start()
    app.run('0.0.0.0', port=FLASK_PORT, debug=False, threaded=True)