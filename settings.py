MODEL_FILENAME = "Qwen3-4B-Instruct-abliterated-Q6_K.gguf" #model used for testing
N_GPU_LAYERS = 4         #Number of layers to offload to GPU (-ngl). If -1, all layers are offloaded.
N_CTX = 8192             #Text context, 0 = from model
N_THREADS = -1           #Number of threads to use for generation, default: None

MAX_TOKENS = None        #default from model
TEMPURATURE = 0.92
TOP_P = 0.5
FREQUENCY_PENALTY = 0.15
PRESENCE_PENALTY = 0.15

THINKING_MODEL = False   #True|False (adds thinking blocks to end of user message)
THINK_MODE = False       #default mode, True|False
THINK = "/think"         #model think tokens to enable if thinking model
NO_THINK = "/no_think"   #model think tokens to disable if thinking model
CHAT_TURNS = 2           #number of turns a chat turns is kept in system prompt

USER_NAME = 'user'       #user name the llm was trained with
BOT_NAME= 'assistant'    #bot name the llm was trained with
SYSTEM_PROMPT = f"You are a helpfull Assistent, Be kind and curtious, respond to the user in a natural speaking way, but always be truthfull."

SYNOCHAT_TOKEN = "Token From Synology Chat Bots settings"
SYNOCHAT_WEBHOOK_URL = "Incoming webhook URL from synology Chat Bots settings"

HOST_IP = "IP Address This Script is Running on"
HOST_PORT = 5015                   #Port you want the server to run on
HOST_API_SECRET = "sk-xxx"         #for OpenAI server Compatability