![Athena](https://raw.githubusercontent.com/thearyadev/Athena/main/graphics/athena.png)
# Usage
Note: To use this bot you must create a discord bot application in your discord developer account, and provide a token to the bot. 

## Providing a token

1. Navigate to `main.py` and open it with a text editor.
2. Replace "YOUR TOKEN HERE" with your discord bot token.
```python
from utils.tools import Athena
from utils.tools.Configuration import configuration
server = Athena()
server.configs.token = "YOUR TOKEN HERE"
server.initialize(mode="-d")
```


This will update the serialized configuration file to hold your token, and will not need to be put in the code again unless the token changes.
4. Proceed to Docker section
## Docker
```bash
cd ./athena-v4/
docker build -t thearyadev/athena:4.0.5 .

docker run athena-v4
```


## Commands
![Commands](https://raw.githubusercontent.com/thearyadev/Athena/main/graphics/help.png)
