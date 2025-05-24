# Chatdb.AI  App
# For mysql and postgresql 
# Deepseek was integrated in appV3 while ollama in appV4


# Clone 
```bash
git clone https://github.com/Incrisz/chat-with-database.git
cd chat-with-database
```
# server requirements (this section is not needed locally)
```bash
sudo apt update
sudo apt install -y build-essential python3-dev libpq-dev libmysqlclient-dev zlib1g-dev libjpeg-dev libfreetype6-dev
sudo apt install python3.12-venv -y
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


# create API keys for DEEPSEEK at 
https://openrouter.ai/settings/keys


# Just copy one
# more deepseek alittle accurate models
```bash
deepseek/deepseek-chat-v3-0324:free
qwen/qwen2.5-vl-3b-instruct:free
qwen/qwen2.5-vl-32b-instruct:free
qwen/qwen2.5-vl-72b-instruct:free
deepseek/deepseek-r1-distill-qwen-32b:free
```
# perfectly accurate models
```bash
nousresearch/deephermes-3-llama-3-8b-preview:free
google/gemma-2-9b-it:free
google/gemma-3-27b-it:free
deepseek/deepseek-prover-v2:free
qwen/qwen-2.5-coder-32b-instruct:free
```


## Other Apps like this are 
https://www.askyourdatabase.com
Vanna Ai
## License
[MIT](https://choosealicense.com/licenses/mit/)
# chat-with-database
