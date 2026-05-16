"""
太初知识宇宙 — 配置层 bootstrap（委托到 runtime/bootstrap.py）

为了向后兼容，保留此文件作为快捷入口。
新代码请直接 from runtime.bootstrap import init_runtime, get_memory
"""

from runtime.bootstrap import *  # noqa: F401, F403
