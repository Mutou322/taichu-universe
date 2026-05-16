"""
太初知识宇宙 — 统一运行时入口（bootloader）

职责:
  1. 初始化 Python 路径（替代所有零散的 sys.path.insert）
  2. 加载全局配置（paths + models）
  3. 提供安全的延迟初始化工厂（MemoryRuntime / ChromaDB / SemanticRuntime）
  4. 统一日志系统
  5. 全局 runtime 上下文

用法:
  from runtime.bootstrap import init_runtime, get_memory, get_semantic

  ctx = init_runtime()         # 启动时调用一次
  mem = get_memory()           # 延迟获取 MemoryRuntime
  sem = get_semantic()         # 延迟获取 SemanticRuntime

环境变量:
  TAICHU_HOME       — 覆盖项目根路径（默认 ~/taichu）
  TAICHU_CONFIG     — 覆盖配置目录（默认 $TAICHU_HOME/config）
  TAICHU_LOG_LEVEL  — 日志级别（默认 INFO）
  TAICHU_API_KEY    — 覆盖 API Key（可选）
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

# ── 路径常量 ──
TAICHU_HOME = Path(os.environ.get("TAICHU_HOME", str(Path.home() / "taichu"))).expanduser().resolve()
TAICHU_CONFIG = Path(os.environ.get("TAICHU_CONFIG", str(TAICHU_HOME / "config"))).expanduser().resolve()
TAICHU_SCRIPTS = (
    Path(os.environ.get("TAICHU_SCRIPTS", str(Path.home() / ".hermes" / "skills" / "wiki-knowledge-base" / "scripts")))
    .expanduser()
    .resolve()
)
TAICHU_VENV = Path(os.environ.get("TAICHU_VENV", str(Path.home() / "taichu_venv"))).expanduser().resolve()

# ── 全局上下文容器 ──
_runtime_context: dict = {}
_memory_instance = None
_semantic_instance = None
_logger: Optional[logging.Logger] = None


def _init_syspath():
    """统一 sys.path 初始化，禁止其他地方再修改"""
    paths_to_add = [
        str(TAICHU_CONFIG),
        str(TAICHU_HOME),
        str(TAICHU_SCRIPTS),
    ]
    # taichu_venv site-packages
    py_ver = f"python3.{sys.version_info.minor}"
    venv_sp = TAICHU_VENV / "lib" / py_ver / "site-packages"
    if venv_sp.exists():
        paths_to_add.append(str(venv_sp))

    for p in paths_to_add:
        if p not in sys.path:
            sys.path.insert(0, p)


def _init_logging():
    """初始化统一日志"""
    global _logger
    level = os.environ.get("TAICHU_LOG_LEVEL", "INFO").upper()
    fmt = "[%(asctime)s] [%(name)s] %(levelname)s: %(message)s"
    logging.basicConfig(level=getattr(logging, level, logging.INFO), format=fmt)
    _logger = logging.getLogger("taichu.bootstrap")
    _logger.info(f"TAICHU_HOME={TAICHU_HOME}")


def init_runtime() -> dict:
    """
    初始化运行时上下文。
    应用启动时调用一次（FastAPI startup event / CLI main / 测试 setup）。

    返回:
        {
            "home": Path,
            "config": Path,
            "logger": Logger,
            "paths": paths module,
            "models": models module,
        }
    """
    global _runtime_context
    if _runtime_context:
        return _runtime_context  # 幂等

    _init_syspath()
    _init_logging()

    # 加载配置模块
    from models import models as _models
    from paths import paths as _paths

    _runtime_context = {
        "home": TAICHU_HOME,
        "config": TAICHU_CONFIG,
        "logger": _logger,
        "paths": _paths,
        "models": _models,
    }
    _logger.info("Runtime initialized")
    return _runtime_context


def get_memory():
    """
    延迟获取 MemoryRuntime 实例。
    支持降级：ChromaDB 不可用时返回降级实例而非崩溃。
    """
    global _memory_instance
    if _memory_instance is not None:
        return _memory_instance

    try:
        from runtime.memory.api import MemoryRuntime

        _memory_instance = MemoryRuntime()
        if _logger:
            _logger.debug("MemoryRuntime initialized")
    except Exception as e:
        if _logger:
            _logger.warning(f"MemoryRuntime init failed, using fallback: {e}")
        _memory_instance = _FallbackMemory()
    return _memory_instance


def get_semantic():
    """延迟获取 SemanticRuntime 实例"""
    global _semantic_instance
    if _semantic_instance is not None:
        return _semantic_instance

    try:
        from runtime.semantic.runtime import SemanticRuntime

        _semantic_instance = SemanticRuntime()
        if _logger:
            _logger.debug("SemanticRuntime initialized")
    except Exception as e:
        if _logger:
            _logger.warning(f"SemanticRuntime init failed: {e}")
        _semantic_instance = None
    return _semantic_instance


# ── 降级实现 ──


class _FallbackMemory:
    """MemoryRuntime 降级实现，ChromaDB 不可用时返回空结果"""

    def search(self, query: str, top_k: int = 5) -> list:
        if _logger:
            _logger.warning(f"[FallbackMemory] search called: {query}")
        return []

    def store(self, doc_id: str, text: str, metadata: dict = None) -> bool:
        if _logger:
            _logger.warning(f"[FallbackMemory] store called: {doc_id}")
        return False

    def delete(self, doc_id: str) -> bool:
        return True

    @property
    def count(self) -> int:
        return 0


# ── 便捷导入 ──
__all__ = [
    "init_runtime",
    "get_memory",
    "get_semantic",
    "TAICHU_HOME",
    "TAICHU_CONFIG",
]
