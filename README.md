# SynologyLLM V2
using Local AI with Synology AI and Synology Chat

Only tested on Windows 11 with python 3.11, builds on llama-ccp-python 

Install
  
  1) install visual studio community 2022 (I checked python development and C++ developement)
  
  2) clone repository
  
  3) create virtual envirement in folder    
    
    python -m venv venv
  
  4) activate virual envirement             
  
    venv/Scripts/activate
 
  5) install the requirements
    
    pip install -r requirements.txt

    -added cuda install directly into requirements, change to your prefered backend as needed
     
Setup

  1) place your LLM in the model folder and copy that file name to the settings file (MODEL_FILENAME="model name.gguf")
  
  2) setup a new bot in your synology chat app
  
  3) copy the Token and the incoming URL to the settings file (SYNOCHAT_TOKEN="Token" and SYNOCHAT_WEBHOOK_URL="incoming url")
        
    -Now is a good time to change the settings file defaults from what I used for testing on my lowend laptop
  
  4) the outgoing URL in synology integration will be http://HOST_IP:HOST_PORT/SynologyLLM change HOST_IP and HOST_PORT to what it is on your local PC your running the model on
  
  5) Use either synologyLLM.bat file or command
  
    python synologyLLM.py
    
    
Features
  
  1) Loads any llama.cpp model that is supported
     
  3) To see list of commands
      
    /commands
  
  4) To Reset your conversation and stored setting    
      
    /reset
  
  5) To change system prompt
      
    /system {new system prompt message}
    
  6) to change how many chat turns is stored in system prompt 

    /chat_turns {number of turns}

  7) To toggle thinking if using a thinking model

    /think {true|false}

  8) Uses a Chat message queue system

  9) Added tool usage and some sample tools in the tools.py file

    -tools included are wiki_tool, ddg_tool, weather_tool, time_tool, news_tool 

  10) Added multiple user capability, it keeps track of all the indivual users settings persistantly 

