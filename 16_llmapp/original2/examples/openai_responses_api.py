import os
from openai import OpenAI
import logging

if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)    
logging.getLogger(__name__).setLevel(logging.DEBUG)

# openaiクライアントの初期化
client = OpenAI()

context = [
    { "role": "user", "content": "What is the capital of France?" }
]
res1 = client.responses.create(
    model="gpt-5",
    input=context,
)

logger.debug("Response 1: %s", res1)

context += res1.output

context += [
    { "role": "user", "content": "And it's population?" }
]

