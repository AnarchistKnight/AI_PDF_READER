import sys
import fitz  # PyMuPDF
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QTextEdit, QLabel, QVBoxLayout,
                             QWidget, QHBoxLayout, QLineEdit)
from PyQt6.QtCore import Qt
import re
from utils import filter_english_and_punctuation
from llm import OllamaLLM, LanguageProcessor
import os
from tqdm import tqdm
import json


FIRST_PAGE = 15
LAST_PAGE = 306
FILE_PATH = "THE COMING WAVE.pdf"
PROCESSED_TEXT_PATH = "processed_texts.json"


def is_valid_string(s):
    # 定义正则表达式，只允许英文字符、数字和标点符号
    pattern = r'[a-zA-Z0-9.,!?;:(){}\[\]\'\"\-— ’]+'

    # 使用 re.fullmatch 检查整个字符串
    return bool(re.fullmatch(pattern, s))


def save_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f)


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


class DocumentText:
    def __init__(self):
        self.paragraphs = [[] for _ in range(LAST_PAGE + 1)]
        self.translated_paragraphs = [[] for _ in range(LAST_PAGE + 1)]
        self.page_summary_100 = ["" for _ in range(LAST_PAGE + 1)]
        self.page_summary_200 = ["" for _ in range(LAST_PAGE + 1)]
        self.page_summary_300 = ["" for _ in range(LAST_PAGE + 1)]
        if os.path.exists(PROCESSED_TEXT_PATH):
            self.load()
        else:
            self.setup()

    def is_empty_page(self, page_index):
        return len(self.paragraphs[page_index]) == 0

    def setup(self):
        pdf_document = fitz.open(FILE_PATH)
        paragraph = ""
        for page_index in range(FIRST_PAGE, LAST_PAGE + 1):
            page = pdf_document.load_page(page_index)
            # 获取文本和其他元素
            blocks = page.get_text("blocks")  # 提取文本内容
            block_index = 0
            for block in blocks:
                block_text = block[4].replace("\n", " ").strip(" ")
                if paragraph == "":
                    paragraph = block_text
                    block_index += 1
                else:
                    paragraph += " " + block_text

                if not paragraph.endswith("."):
                    continue

                self.paragraphs[page_index].append(paragraph)
                paragraph = ""

    def preprocess(self, language_unit):
        for page_index in tqdm(range(LAST_PAGE + 1)):
            for paragraph_english in self.paragraphs[page_index]:
                paragraph_chinese = language_unit.translate(paragraph_english)
                self.translated_paragraphs[page_index].append(paragraph_chinese)
            if len(self.paragraphs[page_index]) > 0:
                summary_100 = language_unit.summarize(self.paragraphs[page_index], 100)
                self.page_summary_100[page_index] = summary_100
                summary_200 = language_unit.summarize(self.paragraphs[page_index], 200)
                self.page_summary_200[page_index] = summary_200
                summary_300 = language_unit.summarize(self.paragraphs[page_index], 300)
                self.page_summary_300[page_index] = summary_300
                self.save()

    def save(self):
        data = {
            "English": self.paragraphs,
            "Chinese": self.translated_paragraphs,
            "100-word summary": self.page_summary_100,
            "200-word summary": self.page_summary_200,
            "300-word summary": self.page_summary_300,
        }
        save_json(data, PROCESSED_TEXT_PATH)

    def load(self):
        data = load_json(PROCESSED_TEXT_PATH)
        self.paragraphs = data["English"]
        self.translated_paragraphs = data["Chinese"]
        self.page_summary_100 = data["100-word summary"]
        self.page_summary_200 = data["200-word summary"]
        self.page_summary_300 = data["300-word summary"]


class PDFViewer(QMainWindow):
    def __init__(self, model_name):
        super().__init__()
        os.system(f"ollama pull {model_name}")
        llm = OllamaLLM(model_name=model_name)
        self.language_unit = LanguageProcessor(llm)

        self.setWindowTitle("The Coming Wave")
        self.setGeometry(50, 50, 1800, 900)

        self.english_line_width = 700
        self.chinese_line_width = 600
        self.chat_line_width = 500
        self.current_page = FIRST_PAGE
        self.document_text = DocumentText()

        self.summary_length = 300
        # 创建主布局
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        text_display_layout = QHBoxLayout()

        # 英文窗口
        english_text_display_layout = QVBoxLayout()
        english_text_display_title = QLabel("英文原文")
        english_text_display_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        english_text_display_layout.addWidget(english_text_display_title)
        self.english_text_display = QTextEdit(self)
        self.english_text_display.setReadOnly(True)
        self.english_text_display.setFixedWidth(self.english_line_width)
        self.english_text_display.setFontPointSize(13)
        english_text_display_layout.addWidget(self.english_text_display)
        text_display_layout.addLayout(english_text_display_layout)
        text_display_layout.setAlignment(english_text_display_layout, Qt.AlignmentFlag.AlignLeft)

        # 中文窗口
        chinese_text_display_layout = QVBoxLayout()
        chinese_text_display_title = QLabel("中文翻译")
        chinese_text_display_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        chinese_text_display_layout.addWidget(chinese_text_display_title)
        self.chinese_text_display = QTextEdit(self)
        self.chinese_text_display.setReadOnly(True)
        self.chinese_text_display.setFixedWidth(self.chinese_line_width)
        self.chinese_text_display.setFontPointSize(13)
        self.chinese_text_display.setMinimumHeight(500)
        chinese_text_display_layout.addWidget(self.chinese_text_display)

        summary_text_display_title = QLabel("中文总结")
        summary_text_display_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        chinese_text_display_layout.addWidget(summary_text_display_title)
        self.summary_text_display = QTextEdit(self)
        self.summary_text_display.setReadOnly(True)
        self.summary_text_display.setFixedWidth(self.chinese_line_width)
        self.summary_text_display.setFontPointSize(13)
        self.summary_text_display.setMinimumHeight(250)
        chinese_text_display_layout.addWidget(self.summary_text_display)
        text_display_layout.addLayout(chinese_text_display_layout)
        text_display_layout.setAlignment(chinese_text_display_layout, Qt.AlignmentFlag.AlignLeft)

        # 聊天窗口
        chat_layout = QVBoxLayout()
        chat_display_title = QLabel("对话记录")
        chat_display_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        chat_layout.addWidget(chat_display_title)
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.chat_display.setFixedWidth(self.chat_line_width)
        self.chat_display.setFontPointSize(13)
        self.chat_display.setMinimumHeight(500)
        chat_layout.addWidget(self.chat_display)
        chat_input_title = QLabel("输入")
        chat_input_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        chat_layout.addWidget(chat_input_title)
        self.chat_input = QTextEdit(self)
        self.chat_input.setPlaceholderText("输入消息...")
        self.chat_input.setFixedWidth(self.chat_line_width)
        # self.chat_input.setFontPointSize(13)
        self.chat_input.setMinimumHeight(250)
        chat_layout.addWidget(self.chat_input)
        self.chat_input_button = QPushButton("发送", self)
        self.chat_input_button.clicked.connect(self.chat)
        self.chat_input_button.setMinimumHeight(40)
        chat_layout.addWidget(self.chat_input_button)
        text_display_layout.addLayout(chat_layout)
        text_display_layout.setAlignment(chat_layout, Qt.AlignmentFlag.AlignLeft)

        # 设置文本窗口布局
        self.layout.addLayout(text_display_layout)

        # 创建按钮布局
        self.button_layout = QHBoxLayout()
        self.first_page_button = QPushButton("第一页", self)
        self.prev_button = QPushButton("上一页", self)
        self.next_button = QPushButton("下一页", self)
        self.last_page_button = QPushButton("最后一页", self)

        self.first_page_button.clicked.connect(self.show_first_page)
        self.prev_button.clicked.connect(self.show_prev_page)
        self.next_button.clicked.connect(self.show_next_page)
        self.last_page_button.clicked.connect(self.show_last_page)

        self.button_layout.addWidget(self.first_page_button)
        self.button_layout.addWidget(self.prev_button)
        self.button_layout.addWidget(self.next_button)
        self.button_layout.addWidget(self.last_page_button)

        self.layout.addLayout(self.button_layout)
        self.show_page(self.current_page)

    def chat(self):
        message = self.chat_input.toPlainText().strip()
        if message:
            self.chat_display.append(f'<span style="color: red;">你</span>: {message}')
            self.chat_input.clear()
            reply = self.language_unit.chat(message)
            self.chat_display.append(f'<span style="color: blue;">AI</span>: {reply}')

    def show_page(self, page_index):
        self.english_text_display.clear()
        for block in self.document_text.paragraphs[page_index]:
            self.english_text_display.append(block + "\n")
        self.chinese_text_display.clear()
        for block in self.document_text.translated_paragraphs[page_index]:
            self.chinese_text_display.append(block + "\n")
        self.summary_text_display.setText(self.document_text.page_summary_200[page_index])

    def show_first_page(self):
        if self.current_page != FIRST_PAGE:
            self.current_page = FIRST_PAGE
            self.show_page(self.current_page)

    def show_prev_page(self):
        if self.current_page > FIRST_PAGE:
            self.current_page -= 1
            while self.document_text.is_empty_page(self.current_page) and self.current_page > FIRST_PAGE:
                self.current_page -= 1
            self.show_page(self.current_page)

    def show_next_page(self):
        if self.current_page < LAST_PAGE:
            self.current_page += 1
            while self.document_text.is_empty_page(self.current_page) and self.current_page < LAST_PAGE:
                self.current_page += 1
            self.show_page(self.current_page)

    def show_last_page(self):
        if self.current_page != LAST_PAGE:
            self.current_page = LAST_PAGE
            self.show_page(self.current_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PDFViewer(model_name="glm4:9b")
    viewer.show()
    sys.exit(app.exec())
    # llm = OllamaLLM(model_name="glm4:9b")
    # language_unit = LanguageProcessor(llm)
    # doc = DocumentText(language_unit)
    # doc.preprocess()
    # p = x.paragraphs[:10]
    # from IPython import embed
    # embed()
