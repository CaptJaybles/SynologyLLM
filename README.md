# synologyLLM
using synology chat with LLMs 

Only tested on Windows 10

Install
  1)install visual studio community 2022 (I checked python development and C++ developement)
  2)clone repository
  3)create virtual envirement in folder    python -m venv venv
  4)activate virual envirement             venv/Scripts/activate
  5)pip install -r requirements.txt
  6)Use either command python synologyLLM.py or use synologyLLM.bat file

Setup
  1)setup a new bot in your synology chat app
  2)copy the Token and the incoming URL to the settings file
  3)the outgoing URL in synology integration will be http://IP_ADDRESS:5010/synologyLLM change IP_ADDRESS to what it is on your local PC your running the model on
  4)place your LLM in the model folder and copy that file name to the setting file


Features
  1)Loads any llama.cpp model that is supported
  2)It has a model reset if the conversation strays command    /reset
  3)It has a continue function if it does finish completely command    /continue 
  4)If system runs to low on memory the model with suspend out of RAM until it is back down again, adjust for your own PC 
    Im using a 8GB laptop and thats what the default settings are setup for
  
