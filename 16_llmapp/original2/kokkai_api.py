import logging

if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)    
logging.getLogger(__name__).setLevel(logging.DEBUG)

kokkai_search_definition = {
  "type": "function",
  "name": "kokkai_search",
  "description": "国会議事録から情報を検索します。XML形式で結果が返されます。",
  "parameters": {
      "type": "object",
      "properties": {
        "words": {
            "type": "string",
            "description": "発言内容等に含まれる言葉を指定可能。部分一致検索。半角スペースを区切り文字として複数指定した場合は、指定した語のAND検索となる。",
        },
      },
      "required": ["words"]
  }
}

def kokkai_search(words: str) -> str:
    """
    国会議事録検索APIを呼び出す関数。
    """
    import requests

    logger.debug("Calling kokkai_search with words: %s", words)

    url = "https://kokkai.ndl.go.jp/api/speech"
    params = {
        "any": words,
    }
    response = requests.get(url, params=params)
    # 送信に使われた最終URL（クエリパラメータを含む・エンコード済み）
    logger.debug("Requested URL: %s", response.url)

    if response.status_code == 200:
        return response.text
    else:
        return f"国会議事録APIの呼び出しに失敗しました。ステータスコード: {response.status_code}"