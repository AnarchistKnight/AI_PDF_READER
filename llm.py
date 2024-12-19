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
        message_history.append({'role': "user", 'content': input_text})
        ollama_response = ollama.chat(model=self.model_name, messages=message_history)
        # Printing out of the generated response
        output_text = ollama_response['message']['content']
        output_text = output_text.replace("\n", "")
        message_history.append({'role': "assistant", 'content': output_text})
        return output_text


class LanguageProcessor:
    def __init__(self, llm):
        self.llm = llm
        self.long_term_history = []

    def chat(self, input_text):
        output_text = self.llm(input_text, self.long_term_history)
        return output_text

    def summarize(self, paragraph_list, summary_length):
        message_history = []
        prompt = ("In the next turn of conversation, you will be given a few paragraphs of an article. You are "
                  "supposed to write a summary of them.")
        self.llm(prompt, message_history)
        requirements = f"""
        1. The summary must be strictly within {summary_length} words.\n
        2. The language of the summary must be simplified Chinese.\n
        3. The summary must be clear, explicit, easily-understood, fluent and smooth.\n
        """
        text = f"""Your summary must strictly follow the requirements below: \n
        {requirements}
        The paragraphs from an article are as follows:"""
        for item in paragraph_list:
            paragraph = item["paragraph"] if type(item)==dict else item
            text += "\n " + paragraph
        summary = self.llm(text, message_history)
        summary = replace_multiple_spaces_with_one(summary)
        return summary

    def translate(self, text_english):
        message_history = []
        requirements = f"""
                1. The translation into simplified Chinese must be easily understood.\n
                2. Only output the translated text. Extra information is unwanted.\n
                """
        prompt = (f"In the next turn of conversation, you will be given a piece of text in English. You are "
                  f"supposed to translate it into simplified Chinese. And you must follow the requirements as "
                  f"follows: \n {requirements}")
        self.llm(prompt, message_history)
        content = f"The text in English is as follows: \n {text_english}"
        text_chinese = self.llm(content, message_history)
        return text_chinese
