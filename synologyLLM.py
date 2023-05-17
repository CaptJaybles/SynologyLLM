from flask import Flask, request
import json
import os
import time
import psutil
import requests
import threading
from synology import OutgoingWebhook
from settings import *
from llama_cpp import Llama

app = Flask(__name__)
model = None
output_text = ""
continued_text= output_text
current_topic = None
inactive_timeout = INACTIVITY_TIMEOUT
last_activity_time = 0  # Variable to track the time of the last activity
high_memory_threshold = HIGH_MEMORY
low_memory_threshold = LOW_MEMORY

def initialize_model():
    global model
    model = Llama(model_path=f"./model/{MODEL_FILENAME}", n_ctx=1024)
    warmup_input = "Human: Name the planets in the solar system? Assistant:"
    model(warmup_input, max_tokens=64, stop=["Human:", "\n"], echo=False)
    model.reset()
    print("Model Loaded")

def check_memory():
    global model
    while True:
        memory_usage = psutil.virtual_memory().percent
        if memory_usage > high_memory_threshold and model is not None:
            model = None
            print("Model suspended due to high memory usage.")
        elif memory_usage <= low_memory_threshold and model is None:
            initialize_model()
            print("Model resumed.")
        time.sleep(1)  # Check memory every second

def send_back_message(user_id, output_text):
    response = output_text
    payload = 'payload=' + json.dumps({
        'text': response,
        "user_ids": [int(user_id)]
    })
    try:
        response = requests.post(INCOMING_WEBHOOK_URL, payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return "Error", 500
    return "success"

def token_gen(token):
    global output_text, continued_text
    output_text += token

def reset_conversation():
    model.reset()

def generate_response(message, user_id, username):
    global last_activity_time
    last_activity_time = time.time()
    if message.startswith("/reset"):
        reset_conversation()
        response = "Wizard Reset"
        return send_back_message(user_id, response)
    elif message.startswith("/continue"):
        global continued_text
        prompt = continued_text
        def generate_message():
            global output_text, continued_text, model
            output = model(prompt, max_tokens=400, temperature=0.8, top_p=0.7, top_k=50, stop=[], repeat_penalty=1.3, frequency_penalty=0.15, presence_penalty=0.15)
            answer = output["choices"][0]["text"]
            token_gen(answer)
            continued_text=output_text.strip(prompt)
            send_back_message(user_id, continued_text)
        threading.Thread(target=generate_message).start()
        return "..."
    else:
        global current_topic
        if current_topic:
            prompt = f"{current_topic} {username}: {message} Assistant:"
        else:
            prompt = f"{username}: {message} Assistant:"
        def generate_message():
            global output_text, model, current_topic
            output_text = ""
            output = model(prompt, max_tokens=400, temperature=0.8, top_p=0.7, top_k=50, stop=[f"{username}:"], repeat_penalty=1.3, frequency_penalty=0.15, presence_penalty=0.15)
            answer = output["choices"][0]["text"]
            token_gen(answer)
            if output_text.endswith("?"):
                current_topic = f"{prompt} Assistant: {output_text}"
            else:
                current_topic = None
            send_back_message(user_id, output_text)
        threading.Thread(target=generate_message).start()
        return "..."

@app.before_request
def check_inactivity():
    global last_activity_time
    if time.time() - last_activity_time > inactive_timeout:
        reset_conversation()
        print("Model Reset")

@app.route('/synologyLLM', methods=['POST'])
def chatbot():
    global model
    token = SYNOCHAT_TOKEN
    webhook = OutgoingWebhook(request.form, token)
    if not webhook.authenticate(token):
        return webhook.createResponse('Outgoing Webhook authentication failed: Token mismatch.')
    message = webhook.text
    user_id = webhook.user_id
    username = webhook.username
    return generate_response(message, user_id, username)

if __name__ == '__main__':
    initialize_model()
    threading.Thread(target=check_memory).start()
    app.run('0.0.0.0', port=FLASK_PORT, debug=False, threaded=True, processes=1)