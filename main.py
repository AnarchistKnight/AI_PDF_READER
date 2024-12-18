from utils import extract_paragraphs_with_page_breaks, print_with_line_length
import argparse
from llm import OllamaLLM, LanguageProcessor
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    # 添加命令行参数
    parser.add_argument('--start_page', type=int, default=18)
    parser.add_argument('--summary_paragraph_num', type=int, default=4)
    parser.add_argument('--summary_length', type=int, default=150)
    parser.add_argument('--model_name', type=str, default="glm4:9b")
    parser.add_argument('--line_length', type=int, default=60)
    # 解析命令行参数
    args = parser.parse_args()

    os.system(f"ollama pull {args.model_name}")
    llm = OllamaLLM(model_name=args.model_name)
    language_unit = LanguageProcessor(llm)

    # 测试函数
    pdf_path = 'THE COMING WAVE.pdf'  # 替换成你的 PDF 文件路径
    paragraphs = extract_paragraphs_with_page_breaks(pdf_path, start_page=args.start_page)

    paragraphs_record = []
    # 输出提取的段落
    for overall_idx, para in enumerate(paragraphs):
        paragraphs_record.append(para)
        if len(paragraphs_record) >= args.summary_paragraph_num:
            summary = language_unit.summarize(paragraphs_record, args.summary_length)
            input("press any key to continue")
            first_para_page_index = paragraphs_record[0]["page index"]
            first_para_block_index = paragraphs_record[0]["block index"]
            last_para_page_index = paragraphs_record[-1]["page index"]
            last_para_block_index = paragraphs_record[-1]["block index"]
            title = (f"summary from page {first_para_page_index} block {first_para_block_index}    "
                     f"to page {last_para_page_index} block {last_para_block_index}")
            print("=" * 15, title, "=" * 15)
            print_with_line_length(summary, args.line_length)
            paragraphs_record = []