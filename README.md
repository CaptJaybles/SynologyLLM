# SynologyLLM V1.8
using synology chat with LLMs

This is the basic usage of local LLM's check out my other repo SynoLangchain for Memory, RAG, and Wiki Q&A 

Only tested on Windows 10, builds on llama-ccp-python 


Install
  
  1) install visual studio community 2022 (I checked python development and C++ developement)
  
  2) clone repository
  
  3) create virtual envirement in folder    
    
    python -m venv venv
  
  4) activate virual envirement             
  
    venv/Scripts/activate
 
  5) install the requirements
    
    pip install -r requirements.txt
     
Setup

  1) place your LLM in the model folder and copy that file name to the settings file
  
  2) setup a new bot in your synology chat app
  
  3) copy the Token and the incoming URL to the settings file
  
  4) the outgoing URL in synology integration will be http://IP_ADDRESS:FLASK_PORT/SynologyLLM change IP_ADDRESS and FLASK_PORT to what it is on your local PC your running the model on
  
  5) Use either synologyLLM.bat file or command
  
    python synologyLLM.py
    
    
Features
  
  1) Loads any llama.cpp model that is supported
  
  2) It has a model reset if the conversation strays command    
      
    /reset
  
  3) prompt continuation command
      
    /continue
    
  4) added prompt override

    /override
    
  5) If system runs to low on memory the model will suspend out of RAM until it is back down again, adjust for your own PC (disabled by default to enable set MEMORY_CHECKER = True) *this feature only works correctly if you are using CPU only

  6) Can change many settings in the settings.py file. ie N_GPU_LAYERS, N_CTX, N_THREADS, LORA_BASE, LORA_PATH, ROPE_FREQ_BASE, ROPE_FREQ_SCALE, MAX_TOKENS, TEMPURATURE, TOP_P, TOP_K, REPEAT_PENALTY, FREQUENCY_PENALTY, PRESENCE_PENALTY, STOP_WORDS

  7) Change the prompts for each individual model, its setup like this
     
     #initial prompt= {SYSTEM_PROMPT}{USER_PROMPT}{message}{USER_END}{BOT_PROMPT}
     
     #Current topic = {USER_PROMPT}{message}{USER_END}{BOT_PROMPT}{answer}
     
     #final prompt = {SYSTEM_PROMPT}{current_topic}\n\n{USER_PROMPT}{message}{USER_END}{BOT_PROMPT}

     SYSTEM_PROMPT = ""
     
     USER_PROMPT = '<|im_start|>user\n'
     
     USER_END = '<|im_end|>\n'
     
     BOT_PROMPT = '<|im_start|>assistant\n'
     

  8) Added message queue system

  9) Added multiple user capability, it should keep track of each individual user and the prior message/response on a individual basis

