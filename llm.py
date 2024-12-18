import ollama
from utils import replace_multiple_spaces_with_one
MODEL_CARDS = ["glm4:9b",
               "qwen2.5:7b", "qwen2.5:14b", "qwen2.5-coder:7b", "qwen2.5-coder:14b",
               "deepseek-coder-v2:16b"]


class OllamaLLM:
    def __init__(self, model_name):
        self.model_name = model_name

    def __call__(self, input_text, message_history):
        # Setting up the model, enabling streaming responses, and defining the input messages
        message_history = [{'role': "user", 'content': input_text}]
        ollama_response = ollama.chat(model=self.model_name, messages=message_history)
        # Printing out of the generated response
        output_text = ollama_response['message']['content']
        output_text = output_text.replace("\n", "")
        message_history.append([{'role': "assistant", 'content': output_text}])
        return output_text


class LanguageProcessor:
    def __init__(self, llm):
        self.llm = llm

    def summarize(self, paragraph_list, summary_length):
        message_history = []
        prompt = (f"In the next turn of conversation, you will be given a few paragraphs. You are supposed "
                  f"to write a summary about them within {summary_length} words. The language must be simplified "
                  f"Chinese. The summary must be clear, explicit, easily-understood, fluent and smooth.")
        self.llm(prompt, message_history)
        text = (f"I want to emphasize again, your returned summary must be in simplified Chinese, within "
                f"{summary_length} words. The paragraphs are as follows:")
        for item in paragraph_list:
            paragraph = item["paragraph"]
            text += "\n " + paragraph
        summary = self.llm(text, message_history)
        summary = replace_multiple_spaces_with_one(summary)
        return summary

    def translate(self, text):
        return
