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

def reset_conversation():
    global output_text, current_topic
    model.reset()
    output_text = ""
    current_topic = None

def generate_response(message, user_id, username):
    global last_activity_time
    last_activity_time = time.time()

    #resets model conversation
    if message.startswith("/reset"):
        reset_conversation()
        response = "Model Reset"
        return send_back_message(user_id, response)

    #reinputs last output to continue generation
    elif message.startswith("/continue"): 
        def generate_message(): 
            global output_text, model
            output = model(output_text, max_tokens=256, temperature=TEMPURATURE, top_p=TOP_P, top_k=TOP_K, stop=[], repeat_penalty=REPEAT_PENALTY, frequency_penalty=FREQUENCY_PENALTY, presence_penalty=PRESENCE_PENALTY)
            answer = output["choices"][0]["text"]
            output_text = answer
            send_back_message(user_id, answer)
        threading.Thread(target=generate_message).start()
        return "..."

    #custom prompt
    elif message.startswith("/override"):
        def generate_message(): 
            global output_text, model
            prompt = message.replace("/override", "").strip()
            output = model(prompt, max_tokens=256, temperature=TEMPURATURE, top_p=TOP_P, top_k=TOP_K, stop=[], repeat_penalty=REPEAT_PENALTY, frequency_penalty=FREQUENCY_PENALTY, presence_penalty=PRESENCE_PENALTY)
            answer = output["choices"][0]["text"]
            output_text = answer
            send_back_message(user_id, answer)
        threading.Thread(target=generate_message).start()
        return "..."

    #normal chat prompt
    else:
        global current_topic
        if current_topic:
            prompt = f'{current_topic} {username}: {message} Assistant:'
        else:
            prompt = f'{username}: {message} Assistant:'
        def generate_message():
            global output_text, model, current_topic
            output = model(prompt, max_tokens=256, temperature=TEMPURATURE, top_p=TOP_P, top_k=TOP_K, stop=[f"{username}:"], repeat_penalty=REPEAT_PENALTY, frequency_penalty=FREQUENCY_PENALTY, presence_penalty=PRESENCE_PENALTY)
            answer = output["choices"][0]["text"]
            output_text = answer
            current_topic = f'{username}: {message} Assistant: {answer}'
            send_back_message(user_id, answer)
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