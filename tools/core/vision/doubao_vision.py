"""豆包 Doubao Vision API 封装（OpenAI 兼容格式）"""

import base64
import os

from openai import OpenAI

# 从 ~/.hermes/config.yaml 中读取 API key 和 endpoint
_HERMES_CONFIG = os.path.join(os.path.expanduser("~"), ".hermes", "config.yaml")

_api_key = None
_base_url = None
_model = None


def _load_config():
    global _api_key, _base_url, _model
    if _api_key:
        return

    import yaml

    try:
        with open(_HERMES_CONFIG) as f:
            cfg = yaml.safe_load(f)
        # vision 在 auxiliary 层级下
        vision_cfg = cfg.get("auxiliary", {}).get("vision", {}) or cfg.get("vision", {})
        _api_key = vision_cfg.get("api_key")
        if _api_key:
            _base_url = vision_cfg.get("base_url", "https://ark.cn-beijing.volces.com/api/v3")
            _model = vision_cfg.get("model", "doubao-vision-pro")
            return
    except Exception:
        pass

    _api_key = os.environ.get("DOUBAO_API_KEY", "")
    _base_url = os.environ.get("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
    _model = os.environ.get("DOUBAO_VISION_MODEL", "doubao-vision-pro")


def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def vision_analyze(image_path: str, prompt: str) -> str:
    """调用豆包 Vision API 分析图片，返回结构化 Markdown 文本"""
    _load_config()

    if not _api_key:
        return "[Vision API 未配置]"

    image_b64 = encode_image(image_path)

    client = OpenAI(
        api_key=_api_key,
        base_url=_base_url,
    )

    response = client.chat.completions.create(
        model=_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}",
                        },
                    },
                ],
            }
        ],
        temperature=0.2,
        max_tokens=4096,
    )

    return response.choices[0].message.content or "[Vision 返回为空]"
