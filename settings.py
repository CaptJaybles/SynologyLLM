#starting with llama-cpp-python version 0.1.79 the model must be in .gguf format if you want to use ggml.bin install llama-cpp-python version 0.1.78 or lower
MODEL_FILENAME = "vicuna-7b-v1.5.Q4_0.gguf" #change to your model of choice
LORA_BASE = None
LORA_PATH = None

FLASK_PORT = 5010
SYNOCHAT_TOKEN = 'Put_your_token_here'
INCOMING_WEBHOOK_URL = "Copy_from_synologychat_incoming_URL"

INACTIVITY_ENABLE = False #True or False(default False is to disable function)
INACTIVITY_TIMEOUT = 86400 # Timeout in seconds for inactivity (10 minutes = 600 seconds)

MEMORY_CHECKER = False #True or False(default False is to disable function)
HIGH_MEMORY = 80 #Adjust the high end threshold as per your requirements (percentage of memory usage)
LOW_MEMORY = 40 #Adjust the low end threshold as per your requirements (percentage of memory usage)

#has the ability for model to use your synology username {username}: so bot can refer to you by name
#the prompt layout is f"{STSTEM_PROMPT}{USER_PROMPT}{message}{BOT_PROMPT}" change prompts to fit your needs
SYSTEM_PROMPT = ''
USER_PROMPT = '{username}: '
BOT_PROMPT = '\n\nAssistant: '

CONTEXT_LENGTH = 1024
MAX_TOKENS = 256
GPU_LAYERS = None
TEMPURATURE = 0.8
TOP_P = 0.7
TOP_K = 50
STOP_WORDS = [f"{username}:"] #comma seperate entries
REPEAT_PENALTY = 1.3
FREQUENCY_PENALTY = 0.15
PRESENCE_PENALTY = 0.15