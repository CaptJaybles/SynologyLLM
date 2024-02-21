MODEL_FILENAME = "dolphin-2_6-phi-2.Q6_K.gguf" #model used for testing
N_GPU_LAYERS = 0 #Number of layers to offload to GPU (-ngl). If -1, all layers are offloaded.
N_CTX = 0 #Text context, 0 = from model
N_THREADS = None #Number of threads to use for generation, default: None
LORA_BASE = None
LORA_PATH = None
ROPE_FREQ_BASE = 0.0 #RoPE base frequency, 0 = from model
ROPE_FREQ_SCALE = 0.0 #RoPE frequency scaling factor, 0 = from model

MAX_TOKENS = 512
TEMPURATURE = 0.92
TOP_P = 0.5
TOP_K = 100
REPEAT_PENALTY = 1.3
FREQUENCY_PENALTY = 0.15
PRESENCE_PENALTY = 0.15
STOP_WORDS = ['<|im_start|>user', '<|im_end|>', '</s>'] #comma seperate entries #change first stop word with user prompt entry

FLASK_PORT = 5010
SYNOCHAT_TOKEN = 'Put_your_token_here'
INCOMING_WEBHOOK_URL = "Copy_from_synologychat_incoming_URL"

#initial prompt= {SYSTEM_PROMPT}{USER_PROMPT}{message}{USER_END}{BOT_PROMPT}
#Current topic = {USER_PROMPT}{message}{USER_END}{BOT_PROMPT}{answer}
#final prompt = {SYSTEM_PROMPT}{current_topic}\n\n{USER_PROMPT}{message}{USER_END}{BOT_PROMPT}

SYSTEM_PROMPT = ''
USER_PROMPT = '<|im_start|>user\n'
USER_END = '<|im_end|>\n'
BOT_PROMPT = '<|im_start|>assistant\n'


MEMORY_CHECKER = False #True or False(unloads model if memory usage is to high)(only works in cpu mode)
HIGH_MEMORY = 80 #Adjust the high end threshold as per your requirements (percentage of memory usage)
LOW_MEMORY = 40 #Adjust the low end threshold as per your requirements (percentage of memory usage)

