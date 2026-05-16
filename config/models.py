"""太初知识宇宙 — 模型配置读取器

统一从 config/models.yaml 读取所有 AI 模型配置和密钥。
单例，所有模块从 models.get() 读取，不得硬编码或从其他文件获取密钥。

用法:
    from models import models
    cfg = models.get("compile")  # 获取编译模型的 {provider, model, api_key, base_url, ...}
    cfg = models.get("embedding")  # 获取嵌入模型配置
    cfg = models.get("query")
    cfg = models.get("reasoning")
    cfg = models.get("vision")
"""

import json
import os
import re
from pathlib import Path

import yaml

_CONFIG_PATH = Path.home() / "taichu" / "config" / "models.yaml"


def _load_api_key(cfg: dict) -> str:
    """读取 API Key，优先级：models.yaml > ov.conf > 环境变量 > hermes config"""
    # 1. models.yaml api.api_key（统一配置入口）
    key = cfg.get("api", {}).get("api_key", "")
    if key:
        return key

    # 2. ov.conf (兼容旧版，api_key 可能嵌套在 embedding/vlm 等对象下)
    ov_conf = Path.home() / ".openviking" / "ov.conf"
    if ov_conf.exists():
        try:
            data = json.loads(ov_conf.read_text())

            def _find_key(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if "key" in k.lower():
                            return v
                        if isinstance(v, (dict, list)):
                            result = _find_key(v)
                            if result:
                                return result
                elif isinstance(obj, list):
                    for item in obj:
                        result = _find_key(item)
                        if result:
                            return result
                return None

            found = _find_key(data)
            if found:
                return found
        except Exception:
            pass

    # 3. 环境变量
    key = os.environ.get("ARK_API_KEY", "")
    if key:
        return key
    key = os.environ.get("AUXILIARY_VISION_API_KEY", "")
    if key:
        return key

    # 4. Hermes config
    hc = Path.home() / ".hermes" / "config.yaml"
    if hc.exists():
        try:
            raw = hc.read_text()
            m = re.search(r"vision:\n\s+api_key:\s*(\S+)", raw)
            if m:
                return m.group(1)
        except Exception:
            pass

    return ""


class _Models:
    """单例模型配置读取器"""

    def __init__(self):
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            self.cfg = yaml.safe_load(f)
        self._api_key = _load_api_key(self.cfg)
        self._base_url = self.cfg.get("api", {}).get("base_url", "")

    def get(self, role: str) -> dict:
        """获取指定角色的模型配置，自动注入 api_key 和 base_url

        参数:
            role: compile / query / reasoning / embedding / vision

        返回:
            {provider, model, api_key, base_url, max_tokens, timeout, ...}
        """
        model_cfg = self.cfg.get("models", {}).get(role, {})
        if not model_cfg:
            return {}

        result = dict(model_cfg)
        result["api_key"] = self._api_key
        result["base_url"] = self._base_url
        return result

    def list_models(self) -> dict:
        """列出所有已配置的模型（不含 api_key）"""
        result = {}
        for role, cfg in self.cfg.get("models", {}).items():
            result[role] = {
                "provider": cfg.get("provider", ""),
                "model": cfg.get("model", ""),
                "purpose": cfg.get("purpose", ""),
            }
        return result

    @property
    def api_key(self) -> str:
        return self._api_key

    @property
    def base_url(self) -> str:
        return self._base_url

    def get_prompt(self, name: str) -> str:
        """获取提示词模板"""
        return self.cfg.get("prompts", {}).get(name, "")


models = _Models()
