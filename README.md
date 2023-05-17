# synology_LLM
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
2)copy the Token and the incoming URL to the settings app
3)the outgoing URL in synology integration will be http://IP_ADDRESS:5010/synologyLLM change IP_ADDRESS to what it is on your local PC your running the model on



Features
1)loads any llama.cpp model that is supported
2)
