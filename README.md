# Jarvis
Seen Iron Man?  It's exactly what you think.

Download the selenium_driver.exe of your choice, it doesn't have to be chromedriver.exe but it has to be called chromedriver.exe and placed in the Jarvis (root) directory.

Create a venv and activate it then run
`python -m pip install -r requirements.txt`

You'll need to add your openAI API key to the secrets.json file

There is a customizable preferences file to configure your code preferences and tell Jarvis your name and where you live and things you like or dislike.
All preferences get sent with every command so be aware lots of preferances equals higher API cost.

Once installed navigate to the directory and run `python launcher.py`
The launcher has a couple of commands you can enter, `all` is a valid argument for start and stop:

start [service]
Pass the name of the file who's service you wish to start without the extention.

stop [service]
Pass the name of the file who's service you wish to stop without the extention.

quit/exit
Stops all services and exits.
