MODEL_FILENAME = "dolphin-llama2-7b.Q4_K_M.gguf" #model used for testing
GPU_LAYERS = 0
LORA_BASE = None
LORA_PATH = None
ROPE_FREQ_BASE = 0.0
ROPE_FREQ_SCALE = 0.0
CONTEXT_LENGTH = 4096
MAX_TOKENS = 1024
TEMPURATURE = 0.92
TOP_P = 0.5
TOP_K = 100
REPEAT_PENALTY = 1.3
FREQUENCY_PENALTY = 0.15
PRESENCE_PENALTY = 0.15
STOP_WORDS = ['{username}:'] #comma seperate entries

FLASK_PORT = 5010
SYNOCHAT_TOKEN = 'Put_your_token_here'
INCOMING_WEBHOOK_URL = "Copy_from_synologychat_incoming_URL"

#has the ability for model to use your synology username '{username}: ' so bot can refer to you by name
#default prompt=f"{SYSTEM_PROMPT}{USER_PROMPT}{message}\n\n{INPUT_PROMPT}{BOT_PROMPT}change USER_PROMPT and BOT_PROMPT to fit your needs
SYSTEM_PROMPT = ""
USER_PROMPT = '{username}: '
INPUT_PROMPT = ""
BOT_PROMPT = 'Assistant: '

INACTIVITY_ENABLE = False #True or False (Resets model after so many minutes)
INACTIVITY_TIMEOUT = 86400 # Timeout in seconds for inactivity (10 minutes = 600 seconds)

MEMORY_CHECKER = False #True or False(unloads model if memory usage is to high)(only works in cpu mode)
HIGH_MEMORY = 80 #Adjust the high end threshold as per your requirements (percentage of memory usage)
LOW_MEMORY = 40 #Adjust the low end threshold as per your requirements (percentage of memory usage)

