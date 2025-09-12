# VS Codeのデバッグ実行で `from chatbot.graph` でエラーを出さない対策
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from flask import Flask, render_template, request, make_response, session 
from chatbot import Chatbot

import logging

if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)  

# Flaskアプリケーションのセットアップ
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション用の秘密鍵
chatbot = Chatbot()

@app.route('/', methods=['GET', 'POST'])
def index():
    # セッションからthread_idを取得、なければ新しく生成してセッションに保存
    if 'thread_id' not in session:
        session['thread_id'] = str(uuid.uuid4())  # ユーザー毎にユニークなIDを生成

    thread_id = session['thread_id']

    # GETリクエスト時はそれまでのチャット内容を表示
    if request.method == 'GET':
        return make_response(render_template('index.html', messages=chatbot.get_messages(thread_id)))

    # ユーザーからのメッセージを取得
    user_message = request.form['user_message']
    
    # ボットのレスポンスを取得
    chatbot.update_messages(thread_id, user_message)

    # メモリからメッセージの取得
    messages = chatbot.get_messages(thread_id)
    logger.debug("Messages to be rendered: %s", messages)

    # レスポンスを返す
    return make_response(render_template('index.html', messages=messages))

@app.route('/clear', methods=['POST'])
def clear():
    # セッションからthread_idを取得して削除
    thread_id = session.pop('thread_id', None)
    # ボットのメモリをクリア
    chatbot.clear_memory(thread_id)
    # 対話履歴を初期化
    response = make_response(render_template('index.html', messages=[]))
    return response

if __name__ == '__main__':
    app.run(debug=True)
