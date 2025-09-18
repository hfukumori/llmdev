import os
from dotenv import load_dotenv
from openai import OpenAI
import logging
import kokkai_api
import json

INITIAL_PROMPT = """あなたはデモンストレーション用のチャットボットです。
Webリンクを提示するときには、日本語のWebサイトを優先してください。
"""

if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)    
logging.getLogger(__name__).setLevel(logging.DEBUG)

# 環境変数を読み込む
load_dotenv(".env")
os.environ['OPENAI_API_KEY'] = os.environ['API_KEY']

# openaiクライアントの初期化
client = OpenAI()

tools = [
    {"type": "web_search"},
    kokkai_api.kokkai_search_definition
]

class Chatbot:
    def __init__(self):
        self.memory = {}  # thread_idごとの対話履歴を保持する辞書

    def update_messages(self, thread_id, user_message):
        thread = self.memory.setdefault(thread_id, self.get_initial_thread())

        # ユーザーメッセージをスレッドに追加
        logger.debug("User message : %s", user_message)
        thread.append({"role": "user", "content": user_message})

        # ここで実際のLLM呼び出しを行い、ボットのレスポンスを取得
        response = client.responses.create(
            model="gpt-5-mini",
            input=thread,
            tools=tools
        )
        logger.debug("-" * 40)
        logger.debug("LLM output response: %s", response.to_dict())
        logger.debug("=" * 40)

        input_list = thread.copy() + response.output
        has_function_call = any(item.type == "function_call" for item in response.output)
        if has_function_call:
            for item in response.output:
                if item.type == "function_call":
                    if item.name == "kokkai_search":
                        # 3. Execute the function logic for kokkai_search
                        kokkai_search_results = kokkai_api.kokkai_search(json.loads(item.arguments).get("words"))

                        # 4. Provide function call results to the model
                        input_list.append({
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": kokkai_search_results
                        })
                        logger.debug("input_list after kokkai_search: %s", input_list)
            response = client.responses.create(
                model="gpt-5-mini",
                input=input_list,
                tools=tools
            )
            logger.debug("LLM output after function call: %s", response.to_dict())
    
        bot_response = response.output_text
        logger.info("Bot response: %s", bot_response)

        # ボットのレスポンスをスレッドに追加
        thread.append({"role": "assistant", "content": bot_response})

        # 更新されたスレッドをメモリに保存
        self.memory[thread_id] = thread
        logger.info("Updated messages for thread_id=%s: %s", thread_id, self.memory[thread_id])

        return bot_response

    def get_messages(self, thread_id):
        messages_in_memory = self.memory.get(thread_id, [])
        logger.debug("Retrieved messages_in_memory for thread_id=%s: %s", thread_id, messages_in_memory)

        messages = []
        for message in messages_in_memory:
            if (message["role"] == "user" or message["role"] == "assistant"):
                class_name = 'user-message' if message["role"] == "user" else 'bot-message'
                messages.append({'class': class_name, 'text': message["content"].replace('\n', '<br>')})

        return messages
    
    def clear_memory(self, thread_id):
        if thread_id in self.memory:
            del self.memory[thread_id]
            logger.info("Cleared memory for thread_id=%s", thread_id)
        else:
            logger.info("No memory to clear for thread_id=%s", thread_id)

    def get_initial_thread(self):
        return [{"role":"system", "content":INITIAL_PROMPT}]