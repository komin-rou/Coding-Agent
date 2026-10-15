import os #Operating System
from dotenv import load_dotenv #dot env
from openai import OpenAI

load_dotenv()

# ==============================
# 模型配置
# ==============================

client = OpenAI(
    api_key=os.getenv("GLM_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4/",
)

MODEL_NAME = os.getenv("GLM_MODEL")


# ==============================
# 通用 LLM 调用
# ==============================

def chat(messages, tools=None):
    # messages: 对话消息列表，格式遵循OpenAI消息规范 [{"role":"user","content":"xxx"},...]

    # 构建请求参数字典 kwargs
    kwargs = {
        "model": MODEL_NAME,
        "messages": messages,
    }

    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    response = client.chat.completions.create(**kwargs)

    return response.choices[0].message