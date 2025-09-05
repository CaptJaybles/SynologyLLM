import json
import os
os.environ["LLAMA_SET_ROWS"] = "1"
import re
import time
import requests
import threading
import queue
import uvicorn
from synology import OutgoingWebhook
from settings import *
from memory import *
from tools import dispatch_tool, ALL_TOOLS
from llama_cpp.server.app import create_app
from llama_cpp.server.settings import ModelSettings, ServerSettings
from openai import OpenAI
from fastapi import APIRouter, Form

entity_memory_store = {}
task_queue = queue.Queue()
memory_queue = queue.Queue()
queue_lock = threading.Semaphore(value=1)
mem_queue_lock = threading.Semaphore(value=1)
thinking_model = THINKING_MODEL

client = OpenAI(base_url=f"http://{HOST_IP}:{HOST_PORT}/v1", api_key=HOST_API_SECRET)

model_settings=ModelSettings(
    model = f"./model/{MODEL_FILENAME}",
    n_gpu_layers = N_GPU_LAYERS,
    n_threads = N_THREADS,
    n_ctx = N_CTX,
    verbose = False,
)
server_settings=ServerSettings(host=HOST_IP, api_key=HOST_API_SECRET)

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
            response = requests.post(SYNOCHAT_WEBHOOK_URL, payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return "Error", 500
    return queue_lock.release()

def generate_response(message, user_id, entity_memory):
    global llm, thinking_model

    thinking_raw = entity_memory.store.get('thinking', default=THINK_MODE)
    thinking = thinking_raw if isinstance(thinking_raw, bool) else str(thinking_raw).strip().lower() == "true"
    system_prompt = entity_memory.store.get('system_prompt', default=SYSTEM_PROMPT)

    if message.startswith("/commands"):
        output = "/reset (resets conversation and memory) /think {true,on | false,off} /chat_turns {integer} /system (set a new system prompt)"
        return send_back_message(user_id, output)

    if message.startswith("/reset"):
        llm.reset
        entity_memory.clear()
        entity_memory.store.clear()
        del entity_memory_store[user_id]
        response = "User System Values Reset."
        return send_back_message(user_id, response)

    if message.startswith("/think"):
        think_match = re.match(r"^/think\w*\s*(.*)", message, re.IGNORECASE)
        think = think_match.group(1).strip().lower() if think_match else ""

        if think in ["on", "true", "1"]:
            entity_memory.store.set('thinking', True)
        elif think in ["off", "false", "0"]:
            entity_memory.store.set('thinking', False)
        else:
            entity_memory.store.set('thinking', False)

        thinking = entity_memory.store.get('thinking', default=THINK_MODE)
        response = f"Thinking set to {thinking}"
        return send_back_message(user_id, response)

    if message.startswith("/system"):
        prompt = message.replace("/system", "").strip().lower()
        entity_memory.store.set('system_prompt', f"{prompt}")
        response = f"New system prompt set"
        return send_back_message(user_id, response)

    if message.startswith("/chat_turns"):
        prompt = message.replace("/chat_turns", "").strip().lower()
        try:
            entity_memory.store.set('chat_turns', int(f"{prompt}"))
            response = f"Number of chat turns set to {prompt}"
            return send_back_message(user_id, response)
        except:
            entity_memory.store.set('chat_turns', CHAT_TURNS)
            response = f"Number of chat turns set to {CHAT_TURNS}"
            return send_back_message(user_id, response)

    topic_key = f"topic_{user_id}"
    stored_topic = entity_memory.store.get(topic_key, default=None)
    if stored_topic == "False":
        current_topic = ""
    else: 
        current_topic = f"\n\n[Current Conversation]\n{stored_topic}"

    if thinking_model:
        if thinking:
            prompt = [
                {"role": "system", "content": f"{system_prompt}{current_topic}"},
                {"role": f"{USER_NAME}", "content": f"{message} {THINK}"},
            ]
        else:
           prompt = [
                {"role": "system", "content": f"{system_prompt}{current_topic}"},
                {"role": f"{USER_NAME}", "content": f"{message} {NO_THINK}"},
            ]
    else:
       prompt = [
            {"role": "system", "content": f"{system_prompt}{current_topic}"},
            {"role": f"{USER_NAME}", "content": f"{message}"},
        ]

    def generate_message(user_id, message, prompt, entity_memory):
        output = client.chat.completions.create(
            messages=prompt,
            model=f"{MODEL_FILENAME}",
            tools=ALL_TOOLS,
            tool_choice="auto",
            max_tokens=MAX_TOKENS,
            temperature=TEMPURATURE,
            top_p=TOP_P,
            frequency_penalty=FREQUENCY_PENALTY,
            presence_penalty=PRESENCE_PENALTY,
            stream=False
        )
        choice = output.choices[0]
        msg_content = choice.message.content
        tool_call_match = re.search(r"<tool_call>(.*?)</tool_call>", msg_content, re.DOTALL)
        if tool_call_match:
            try:
                tool_json = json.loads(tool_call_match.group(1).strip())
                tool_name = tool_json["name"]
                args = tool_json.get("arguments", {})
                result = dispatch_tool(tool_name, args, user_id)
                followup_output = client.chat.completions.create(
                    messages=[
                        *prompt,
                        {"role": "assistant", "content": msg_content},
                        {"role": "assistant", "content": f"<tool_result name='{tool_name}'>\n{result}\n</tool_result>"},
                    ],
                    model=f"{MODEL_FILENAME}",
                    max_tokens=MAX_TOKENS,
                    stream=False
                )   
                answer = followup_output.choices[0].message.content
            except Exception as e:
                answer = f"Tool execution error: {str(e)}"
        else:
            answer = choice.message.content
        if thinking_model:
            answer = re.sub(r"<think>.*?</think>\n*", "", answer, flags=re.DOTALL).strip()
        memory_queue.put((user_id, answer, message, entity_memory))
        return send_back_message(user_id, answer)
    threading.Thread(target=generate_message, args=(user_id, message, prompt, entity_memory)).start()
    return "..."

def memory_function(user_id, answer, message, entity_memory):
    try:
        new_turn = f"{USER_NAME}\n{message}\n{BOT_NAME}\n{answer}"
        topic_key = f"topic_{user_id}"
        stored_topic = entity_memory.store.get(topic_key, default=None)
        chat_turns = entity_memory.store.get('chat_turns', default=CHAT_TURNS)
        if stored_topic not in ("False", "None", "", None, False):
            turns = stored_topic.strip().split("\n[metadata:")
            turns = [("[metadata:" + t).strip() for t in turns if t.strip()]
            turns.append(new_turn)
            if chat_turns==0:
                current_topic = ""
            else:
                if len(turns) > chat_turns:
                    turns = turns[-chat_turns:]
                current_topic = "\n".join(turns)
        else:
            if chat_turns==0:
                current_topic = ""
            else:
                current_topic = new_turn
        entity_memory.store.set(topic_key, current_topic)
    except Exception as e:
        print(f"Error in Memory Function: {e}")
    finally:
        mem_queue_lock.release()

router = APIRouter()
@router.post("/SynologyLLM")
def chatbot(
    token: str = Form(...),
    user_id: str = Form(...),
    username: str = Form(...),
    post_id: str = Form(...),
    timestamp: str = Form(...),
    text: str = Form(...)
):
    data = {
        "token": token,
        "user_id": user_id,
        "username": username,
        "post_id": post_id,
        "timestamp": timestamp,
        "text": text,
    }
    client_token = SYNOCHAT_TOKEN
    webhook = OutgoingWebhook(data, client_token)
    if not webhook.authenticate(token):
        return webhook.createResponse('Outgoing Webhook authentication failed: Token mismatch.')
    message = webhook.text
    user_id = webhook.user_id
    if user_id not in entity_memory_store:
        entity_memory_store[user_id] = EntityMemory(session_id=user_id)
    entity_memory = entity_memory_store[user_id]
    stored_topic = entity_memory.store.get(f"topic_{user_id}", default=None)
    if stored_topic is None:
        entity_memory.store.set(f"topic_{user_id}", "False")
        entity_memory.store.set('thinking', THINK_MODE)
        entity_memory.store.set('system_prompt', SYSTEM_PROMPT)
        entity_memory.store.set('chat_turns', CHAT_TURNS)
    task_queue.put((message, user_id, entity_memory))
    return "Task queued for processing"

def process_tasks():
    while True:
        queue_lock.acquire()
        try:
            message, user_id, entity_memory = task_queue.get()
            generate_response(message, user_id, entity_memory)
        finally:
            task_queue.task_done()
        time.sleep(0.5)

def process_memory():
    while True:
        mem_queue_lock.acquire()
        try:
            user_id, answer, message, entity_memory = memory_queue.get()
            threading.Thread(target=memory_function, args=(user_id, answer, message, entity_memory)).start()
        finally:
            memory_queue.task_done()
        time.sleep(0.5)

if __name__ == '__main__':
    app = create_app(server_settings=server_settings, model_settings=[model_settings])
    app.include_router(router)
    processing_tasks = threading.Thread(target=process_tasks, daemon=True).start()
    processing_memory = threading.Thread(target=process_memory).start()

    uvicorn.run(app, host=HOST_IP, port=HOST_PORT)


