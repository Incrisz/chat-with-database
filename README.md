# Chatdb.AI  App

# Clone 
```bash
git clone https://github.com/Incrisz/chat-with-database.git
cd chat-with-database
```
# server requirements (this section is not needed locally)
```bash
sudo apt update
sudo apt install -y build-essential python3-dev libpq-dev libmysqlclient-dev zlib1g-dev libjpeg-dev libfreetype6-dev
sudo apt install python3.12-venv
sudo apt install python3-pip -y

```

# Install
```bash
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

# Configure
You can configure secrets in `.env` .
```bash
cp .env.example .env
```

# Run
```bash
streamlit run appV2.py
```


## Other Apps like this are 
https://www.askyourdatabase.com
Vanna Ai
## License
[MIT](https://choosealicense.com/licenses/mit/)
# chat-with-database
