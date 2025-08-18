# VS Codeのデバッグ実行で `from chatbot.graph` でエラーを出さない対策
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, make_response
from rag import get_bot_response, get_messages_list, clear_messages

# Flaskアプリケーションのセットアップ
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    # GETリクエスト時は初期メッセージ表示
    if request.method == 'GET':
        # 対話履歴を初期化
        clear_messages()
        response = make_response(render_template('index.html', messages=[]))
        return response

    # ユーザーからのメッセージを取得
    user_message = request.form['user_message']
    
    # ボットのレスポンスを取得（chat_historyに保持）
    get_bot_response(user_message)

    # chat_historyからメッセージの取得
    messages = get_messages_list()

    # レスポンスを返す
    return make_response(render_template('index.html', messages=messages))

@app.route('/clear', methods=['POST'])
def clear():
    # 対話履歴を初期化
    clear_messages()
    response = make_response(render_template('index.html', messages=[]))
    return response

if __name__ == '__main__':
    app.run(debug=True)
