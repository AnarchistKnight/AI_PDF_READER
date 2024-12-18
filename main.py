from utils import extract_paragraphs_with_page_breaks, print_with_line_length
import argparse
from llm import OllamaLLM, LanguageProcessor
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    # 添加命令行参数
    parser.add_argument('--start_page', type=int, default=18)
    parser.add_argument('--summary_paragraph_num', type=int, default=8)
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

    paragraph_record = []
    paragraph_indices = []
    # 输出提取的段落
    for overall_idx, para in enumerate(paragraphs):
        paragraph_record.append(para)
        paragraph_indices.append(overall_idx)
        if len(paragraph_record) >= args.summary_paragraph_num:
            summary = language_unit.summarize(paragraph_record, args.summary_length)
            input("press any key to continue")
            first_para_page_idx = paragraph_record[0]["page index"]
            first_para_block_idx = paragraph_record[0]["block index"]
            last_para_page_idx = paragraph_record[-1]["page index"]
            last_para_block_idx = paragraph_record[-1]["block index"]
            min_para_idx = paragraph_indices[0]
            max_para_idx = paragraph_indices[-1]
            title = (f"summary ---- page {first_para_page_idx} block {first_para_block_idx} para {min_para_idx} ---- "
                     f"to page {last_para_page_idx} block {last_para_block_idx} para {max_para_idx}")
            print("=" * 15, title, "=" * 15)
            print_with_line_length(summary, args.line_length)
            paragraph_record = []
            paragraph_indices = []
            print("")
