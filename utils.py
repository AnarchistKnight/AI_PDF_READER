import fitz  # PyMuPDF
import re


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
