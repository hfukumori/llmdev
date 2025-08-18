# 必要なモジュールをインポート
import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai import OpenAI

# 環境変数の取得
load_dotenv(".env")
os.environ['OPENAI_API_KEY']  = os.environ['API_KEY']

# モデル名
MODEL_NAME = "gpt-4o-mini"

# Indexの構築
current_directory = os.path.dirname(os.path.abspath(__file__))
documents = SimpleDirectoryReader(f'{current_directory}/data/text').load_data()
index = VectorStoreIndex.from_documents(documents)

# Chat Engineの作成
llm = OpenAI(model=MODEL_NAME)
chat_engine = index.as_chat_engine(llm=llm)

# ===== 応答を返す関数 =====
def get_bot_response(user_message):
    """
    ユーザーのメッセージに基づき、ボットの応答を取得します。
    """
    response = chat_engine.chat(user_message)
    return response.response

def get_messages_list():
    """
    チャット履歴からメッセージのリストを取得します。
    """
    messages = []
    for message in chat_engine.chat_history:
        if message.role == "user" and message.content != None:
            # ユーザーからのメッセージ
            messages.append({'class': 'user-message', 'text': message.content.replace('\n', '<br>')})
        elif message.role == "assistant" and message.content != None:
            # ボットからのメッセージ（最終回答）
            messages.append({'class': 'bot-message', 'text': message.content.replace('\n', '<br>')})
    return messages

def clear_messages():
    """
    チャット履歴をクリアします。
    """
    chat_engine.chat_history.clear()
