# Chatdb.AI  App

# Clone 
```bash
git clone https://github.com/Incrisz/chat-with-database.git
cd chat-with-database
```
# server requirements (this section is not needed locally)
```bash
sudo apt update
sudo apt update
sudo apt install -y build-essential python3-dev libpq-dev libmysqlclient-dev zlib1g-dev libjpeg-dev libfreetype6-dev

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
streamlit run app.py
```


## Other Apps like this are 
https://www.askyourdatabase.com
Vanna Ai
## License
[MIT](https://choosealicense.com/licenses/mit/)
# chat-with-database
