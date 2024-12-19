import sys
import fitz  # PyMuPDF
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QTextEdit, QLabel,
                             QFileDialog, QVBoxLayout, QWidget, QHBoxLayout)
from PyQt6.QtCore import Qt
import re
from utils import filter_english_and_punctuation
from llm import OllamaLLM, LanguageProcessor
import os


FIRST_PAGE = 15
LAST_PAGE = 306
FILE_PATH = "THE COMING WAVE.pdf"


def is_valid_string(s):
    # 定义正则表达式，只允许英文字符、数字和标点符号
    pattern = r'[a-zA-Z0-9.,!?;:(){}\[\]\'\"\-— ’]+'

    # 使用 re.fullmatch 检查整个字符串
    return bool(re.fullmatch(pattern, s))


class PageText:
    def __init__(self, page_index, page):
        return


class DocumentText:
    def __init__(self):
        self.paragraphs = [[] for _ in range(LAST_PAGE + 1)]
        self.setup()

    def __getitem__(self, index):
        return self.paragraphs[index]

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


class PDFViewer(QMainWindow):
    def __init__(self, model_name):
        super().__init__()
        os.system(f"ollama pull {model_name}")
        self.llm = OllamaLLM(model_name=model_name)
        self.language_unit = LanguageProcessor(self.llm)

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
        self.chat_input.setFixedWidth(self.chat_line_width)
        self.chat_input.setFontPointSize(13)
        self.chat_input.setMinimumHeight(250)
        chat_layout.addWidget(self.chat_input)
        self.chat_input_button = QPushButton("发送", self)
        chat_layout.addWidget(self.chat_input_button)
        self.chat_input_button.setMinimumHeight(40)
        text_display_layout.addLayout(chat_layout)
        text_display_layout.setAlignment(chat_layout, Qt.AlignmentFlag.AlignLeft)

        # 设置文本窗口布局
        self.layout.addLayout(text_display_layout)

        # 创建按钮布局
        self.button_layout = QHBoxLayout()
        self.first_page_button = QPushButton("第一页", self)
        self.prev_button = QPushButton("上一页", self)
        self.translate_button = QPushButton("翻译", self)
        self.summary_button = QPushButton("总结", self)
        self.next_button = QPushButton("下一页", self)
        self.last_page_button = QPushButton("最后一页", self)

        self.first_page_button.clicked.connect(self.show_first_page)
        self.prev_button.clicked.connect(self.show_prev_page)
        self.translate_button.clicked.connect(self.show_translated_page)
        self.summary_button.clicked.connect(self.show_summary_page)
        self.next_button.clicked.connect(self.show_next_page)
        self.last_page_button.clicked.connect(self.show_last_page)

        self.button_layout.addWidget(self.first_page_button)
        self.button_layout.addWidget(self.prev_button)
        self.button_layout.addWidget(self.translate_button)
        self.button_layout.addWidget(self.summary_button)
        self.button_layout.addWidget(self.next_button)
        self.button_layout.addWidget(self.last_page_button)

        self.layout.addLayout(self.button_layout)
        self.show_page(self.current_page)

        self.translated = False
        self.summarized = False

    def reset_auxiliary_displays(self):
        self.translated = False
        self.chinese_text_display.clear()
        self.summarized = False
        self.summary_text_display.clear()

    def show_page(self, page_number):
        blocks = self.document_text[page_number]  # 提取文本内容
        self.render_page(blocks)

    def render_page(self, blocks):
        # 清除文本编辑器
        self.english_text_display.clear()
        # 绘制文本
        for block in blocks:
            self.english_text_display.append(block + "\n")

    def show_first_page(self):
        if self.current_page != FIRST_PAGE:
            self.current_page = FIRST_PAGE
            self.show_page(self.current_page)
            self.reset_auxiliary_displays()

    def show_translated_page(self):
        if not self.translated:
            page_paragraphs = self.document_text[self.current_page]
            for paragraph_english in page_paragraphs:
                paragraph_chinese = self.language_unit.translate(paragraph_english)
                self.chinese_text_display.append(paragraph_chinese + "\n")
            self.translated = True

    def show_summary_page(self):
        if not self.summarized:
            page_paragraphs = self.document_text[self.current_page]
            summary = self.language_unit.summarize(page_paragraphs, self.summary_length)
            self.summary_text_display.setText(summary)
            self.summarized = True

    def show_prev_page(self):
        if self.current_page > FIRST_PAGE:
            self.current_page -= 1
            self.show_page(self.current_page)
            self.reset_auxiliary_displays()

    def show_next_page(self):
        if self.current_page < LAST_PAGE:
            self.current_page += 1
            self.show_page(self.current_page)
            self.reset_auxiliary_displays()

    def show_last_page(self):
        if self.current_page != LAST_PAGE:
            self.current_page = LAST_PAGE
            self.show_page(self.current_page)
            self.reset_auxiliary_displays()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PDFViewer(model_name="glm4:9b")
    viewer.show()
    sys.exit(app.exec())
    # x = DocumentText()
    # p = x.paragraphs[:10]
    # from IPython import embed
    # embed()
