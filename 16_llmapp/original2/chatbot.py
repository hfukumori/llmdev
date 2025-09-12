import os
from dotenv import load_dotenv
from openai import OpenAI
import logging

if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)    
logging.getLogger(__name__).setLevel(logging.DEBUG)

# 環境変数を読み込む
load_dotenv(".env")
os.environ['OPENAI_API_KEY'] = os.environ['API_KEY']

# openaiクライアントの初期化
client = OpenAI()

class Chatbot:
    def __init__(self):
        self.memory = {}  # thread_idごとの対話履歴を保持する辞書

    def update_messages(self, thread_id, user_message):
        thread = self.memory.setdefault(thread_id, self.get_initial_thread())

        # ユーザーメッセージをスレッドに追加
        logger.debug("User message : %s", user_message)
        thread.append({"role": "user", "content": user_message})

        # ここで実際のLLM呼び出しを行い、ボットのレスポンスを取得
        completion = client.chat.completions.create(
            model="gpt-5-mini",
            messages=thread,
        )
        bot_response = completion.choices[0].message.content
        logger.debug("Bot response: %s", bot_response)

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
        for mim in messages_in_memory:
            if (mim["role"] == "user"):
                messages.append({'class': 'user-message', 'text': mim["content"].replace('\n', '<br>')})
            elif (mim["role"] == "assistant"):
                messages.append({'class': 'bot-message', 'text': mim["content"].replace('\n', '<br>')})
        return messages
    
    def clear_memory(self, thread_id):
        if thread_id in self.memory:
            del self.memory[thread_id]
            logger.info("Cleared memory for thread_id=%s", thread_id)
        else:
            logger.info("No memory to clear for thread_id=%s", thread_id)

    def get_initial_thread(self):
        return [{"role": "system", "content": "You are a helpful assistant."}]