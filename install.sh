pip config set global.index-url "http://mirrors.cloud.tencent.com/pypi/simple"
pip config set global.trusted-host "mirrors.cloud.tencent.com"
python.exe -m pip install --upgrade pip
pip install ollama
pip install pymupdf