"""太初知识宇宙 — 统一路径配置中心

单例，所有模块从 paths.get() 读取路径，不得硬编码。
"""

from pathlib import Path

import yaml

_CONFIG_PATH = Path.home() / "taichu" / "config" / "paths.yaml"


class _Paths:
    """单例配置读取器"""

    def __init__(self):
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            self.cfg = yaml.safe_load(f)

    def get(self, *keys: str) -> Path:
        """按层级读取路径，返回 Path 对象

        用法:
            paths.get("ingest", "raw")     → ~/taichu/ingest/raw
            paths.get("knowledge", "wiki") → ~/taichu/knowledge/wiki
        """
        node = self.cfg
        for k in keys:
            node = node[k]
        return Path(node).expanduser()

    @property
    def root(self) -> Path:
        return self.get("root")

    @property
    def raw_dir(self) -> Path:
        return self.get("ingest", "raw")

    @property
    def inbox_dir(self) -> Path:
        return self.get("ingest", "inbox")

    @property
    def wiki_dir(self) -> Path:
        return self.get("knowledge", "wiki")

    @property
    def chroma_dir(self) -> Path:
        return self.get("storage", "chroma")

    @property
    def log_dir(self) -> Path:
        return self.get("logs", "root")

    @property
    def kb_models(self) -> Path:
        """kb_models.py 脚本路径"""
        return self.get("scripts")

    def __getattr__(self, name):
        """支持属性链访问，如 paths.ingest.inbox → paths.get("ingest", "inbox")"""
        if name.startswith("_"):
            raise AttributeError(name)

        # 返回一个代理对象，支持进一步 .xxx 访问
        class _PathProxy:
            def __init__(self, parent, key):
                self._parent = parent
                self._key = key

            def __getattr__(self, sub):
                if sub.startswith("_"):
                    raise AttributeError(sub)
                return self._parent.get(self._key, sub)

            def __repr__(self):
                return f"<PathProxy: {self._key}>"

        return _PathProxy(self, name)


paths = _Paths()
