本项目为专门适配 [《The Comming Wave》](https://github.com/AnarchistKnight/AI_reader_of_The_Coming_Wave/blob/4c820c8ea4aaa2682cedf4a3df50099248332ba1/THE%20COMING%20WAVE.pdf})的 AI 阅读器，通过 Ollama 在本地调用大模型来实现智能交互。您可对**全书**或**当前阅读页**直接提问。

## 使用示例
![image](https://github.com/user-attachments/assets/2d51e7cd-0826-4f6d-8074-0a4083e22e50)

## 安装
1. 首先下载 [Ollama](https://ollama.com/download)
2. 拉取本项目
```
git clone https://github.com/AnarchistKnight/AI_reader_of_The_Coming_Wave.git
```
5. 打开项目，可使用 pycharm settings 中选择 python interpreter, 也可以在 terminal 中输入'python -m venv venv', 来配置 python 环境
6. 在 terminal 中直接运行 [bash install.sh](https://github.com/AnarchistKnight/AI_reader_of_The_Coming_Wave/blob/56b829348c31c1920c2bc5955c9a2a931e6015b9/install.sh) 或逐个键入以下命令
```
python.exe -m pip install --upgrade pip
pip install setuptools
pip install ollama
pip install pymupdf
pip install Pillow
pip install screeninfo
pip install pyqt6
pip install tqdm
pip install psutil
pip install gputil
```
5. terminal 输入 ollama serve 开启 ollama
6. 另开一个 terminal 输入以下之一，请根据显卡显存大小选择模型
```
ollama pull glm4:9b                     # 5.5 GB 
ollama pull qwen2.5-coder:14b           # 9.0 GB
ollama pull qwen2.5:7b                  # 4.7 GB
ollama pull qwen2.5-coder:32b           # 19 GB
ollama pull qwen2.5-coder:latest        # 4.7 GB
ollama pull llama3.2:1b                 # 1.3 GB
ollama pull llama3.2:3b                 # 2.0 GB
ollama pull llama3.2:latest             # 2.0 GB
ollama pull qwen2.5:latest              # 4.7 GB
ollama pull x/llama3.2-vision:latest    # 7.9 GB
ollama pull llava:latest                # 4.7 GB
```
