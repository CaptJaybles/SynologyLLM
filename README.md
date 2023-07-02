# synologyLLM
using synology chat with LLMs

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
  
Optional GPU Support for CUBLAS 

  1) Open powershell in folder that has all the files
    
    python -m venv venv

    pip uninstall -y llama-cpp-python

    $Env:LLAMA_CUBLAS = "1"
     
    $Env:FORCE_CMAKE = "1"
     
    $Env:CMAKE_ARGS="-DLLAMA_CUBLAS=on"
     
    pip install llama-cpp-python --no-cache-dir

  2) change GPU layers in settings to what will fit your GPU
     
Setup

  1) place your LLM in the model folder and copy that file name to the settings file
  
  2) setup a new bot in your synology chat app
  
  3) copy the Token and the incoming URL to the settings file
  
  4) the outgoing URL in synology integration will be http://IP_ADDRESS:FLASK_PORT/synologyLLM change IP_ADDRESS and FLASK_PORT to what it is on your local PC your running the model on
  
  5) Use either synologyLLM.bat file or command
  
    python synologyLLM.py
    
    
Features
  
  1) Loads any llama.cpp model that is supported
  
  2) It has a model reset if the conversation strays command    
      
    /reset
  
  3) built in auto reset after 1 Day of inactivity can be adjusted to longer or shorter in the settings (INACTIVITY_TIMEOUT)
     (disabled by default to enable set INACTIVITY_ENABLE = True)
  
  5) prompt continuation command
      
    /continue
    
  5) added prompt override

    /override
    
  6) If system runs to low on memory the model will suspend out of RAM until it is back down again, adjust for your own PC (disabled by default to enable set MEMORY_CHECKER = True) *this feature only works correctly if you are using CPU only

  7) Added ability to change model context length CONTEXT_LENGTH and model max tokens generated MAX_TOKENS

  
TODO

  1) Add support for message queue so more than one person can use service at a time
  
  2) Anything else I or anybody else can help with
