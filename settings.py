#MODEL_FILENAME = "ggml-vic7b-q4_0.bin"
#MODEL_FILENAME = "Wizard-Vicuna-7B-Uncensored.ggmlv2.q4_0.bin"

SYNOCHAT_TOKEN = 'Put_your_token_here'

INCOMING_WEBHOOK_URL = "Copy_from_synologychat_incoming_URL"

INACTIVITY_TIMEOUT = 86400 # Timeout in seconds for inactivity (10 minutes = 600 seconds)

MEMORY_CHECKER = False #True or False(default False is to disable function)

HIGH_MEMORY = 100 #Adjust the high end threshold as per your requirements (percentage of memory usage)

LOW_MEMORY = 100 #Adjust the low end threshold as per your requirements (percentage of memory usage)

FLASK_PORT = 5010

TEMPURATURE = 0.8

TOP_P = 0.7

TOP_K = 50

REPEAT_PENALTY = 1.3

FREQUENCY_PENALTY = 0.15

PRESENCE_PENALTY = 0.15