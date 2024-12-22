import fitz  # PyMuPDF
import re
import GPUtil


def filter_english_and_punctuation(text):
    # 定义正则表达式，匹配英文字符和常见英文标点
    pattern = r'[a-zA-Z0-9.,!?;:(){}\[\]\'\"\- ]+'

    # 使用 re.findall() 来提取匹配的字符
    filtered_text = ''.join(re.findall(pattern, text))

    return filtered_text


def extract_paragraphs_with_page_breaks(pdf_path, start_page):
    # 打开 PDF 文件
    doc = fitz.open(pdf_path)

    paragraph_list = []
    paragraph = ""

    # 遍历所有页面
    for page_index in range(start_page, doc.page_count):
        page = doc.load_page(page_index)

        # 获取页面的文本块
        blocks = page.get_text("blocks")

        for block_index, block in enumerate(blocks):
            text = filter_english_and_punctuation(block[4]).strip() # 获取文本内容并去掉前后空白

            if text == "":
                continue

            paragraph += text

            if paragraph.endswith("."):
                paragraph_list.append({"page index": page_index + 1,
                                       "block index": block_index,
                                       "paragraph": paragraph})
                paragraph = ""

    return paragraph_list


def print_with_line_length(text, line_length):
    # 遍历文本并按指定的行长打印
    for i in range(0, len(text), line_length):
        print(text[i: i + line_length])


def replace_multiple_spaces_with_one(text):
    # 使用正则表达式将多个空格替换成单个空格
    return re.sub(r'\s+', ' ', text)


def check_integrated_gpu():
    integrated_gpu = False
    for device in GPUtil.getGPUs():
        if device.name.lower() == 'intel':
            integrated_gpu = True
            break
    return integrated_gpu


def get_gpu_info():
    gpus = GPUtil.getGPUs()
    if not gpus:
        return None  # 没有找到可用的显卡

    gpu_info = []
    for gpu in gpus:
        info = {
            'name': gpu.name,
            'memoryTotal': gpu.memoryTotal,
            'memoryFree': gpu.memoryFree,
            'memoryUsed': gpu.memoryUsed,
            'temperature': gpu.temperature,
        }
        gpu_info.append(info)
    return gpu_info


def print_gpu_info():
    has_integrated_gpu = check_integrated_gpu()
    gpu_info = get_gpu_info()

    print(f"是否有集成显卡: {'是' if has_integrated_gpu else '否'}")
    print("显卡信息:")
    for info in gpu_info:
        print(f"名称: {info['name']}, 显存总量: {info['memoryTotal']} MB, "
              f"显存已用: {info['memoryUsed']} MB, "
              f"显存剩余: {info['memoryFree']} MB, "
              f"温度: {info['temperature']} °C")


def get_recommended_llm():
    model_name = "qwen2.5:0.5b"
    gpu_info = get_gpu_info()
    if gpu_info and len(gpu_info) > 0:
        memory = gpu_info[0]['memoryTotal']
        if memory > 8192:
            model_name = "glm4:9b"
        elif memory > 4096:
            model_name = "qwen2.5:3b"
        else:
            model_name = "qwen2.5:1.5b"
    return model_name
