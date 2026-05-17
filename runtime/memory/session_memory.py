"""SessionMemory — 跨会话记忆管理器

为所有 Agent 提供持久化会话记忆：对话、决策、心得按 agent_id 归集，
语义检索跨会话召回。重启不丢失，所有 Agent 通过统一 API 读写。

使用 ChromaDB 的 evomind 集合（代码中已引用但未实际使用）。
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from config.paths import paths
from storage.vector.chroma_store import ChromaStore

logger = logging.getLogger(__name__)

# ── 常量 ──

MEMORY_COLLECTION = "evomind"
DEFAULT_AGENT = "taichu"

# 重要性标签
IMPORTANCE_LOW = 0.3  # 日常对话
IMPORTANCE_NORMAL = 0.6  # 决策/事实
IMPORTANCE_HIGH = 0.9  # 重要心得/用户偏好

# 记忆类型
TYPE_CONVERSATION = "conversation"
TYPE_DECISION = "decision"
TYPE_INSIGHT = "insight"
TYPE_SUMMARY = "summary"
TYPE_USER_PREFERENCE = "user_preference"


class SessionMemory:
    """跨会话记忆管理器"""

    def __init__(self) -> None:
        self._store: Optional[ChromaStore] = None
        self._embedder = None

    # ── 延迟初始化 ──

    def _get_store(self) -> ChromaStore:
        if self._store is None:
            self._store = ChromaStore(str(paths.chroma_dir), MEMORY_COLLECTION)
        return self._store

    def _get_embedder(self):
        if self._embedder is None:
            from storage.embeddings.embedder import Embedder

            self._embedder = Embedder()
        return self._embedder

    # ── 写 ──

    def save(
        self,
        content: str,
        *,
        agent_id: str = DEFAULT_AGENT,
        session_id: str = "",
        memory_type: str = TYPE_CONVERSATION,
        importance: float = IMPORTANCE_NORMAL,
        summary: str = "",
        metadata: Optional[dict] = None,
    ) -> str:
        """保存一条记忆到 ChromaDB。

        Args:
            content: 记忆内容（对话文本/决策/心得）。
            agent_id: Agent 标识（hermes/claude-code/taichu）。
            session_id: 会话 ID（不传则自动生成）。
            memory_type: 类型（conversation/decision/insight/...）。
            importance: 重要性 0-1（低0.3/正常0.6/高0.9）。
            summary: 简短摘要（不传则截取 content 前 60 字）。
            metadata: 额外元数据（与已有字段合并）。

        Returns:
            记忆条目的 ID。
        """
        if not session_id:
            session_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        mem_id = f"{agent_id}_{session_id}_{uuid.uuid4().hex[:8]}"
        ts = datetime.now(timezone.utc).isoformat()

        meta = {
            "agent_id": agent_id,
            "session_id": session_id,
            "type": memory_type,
            "timestamp": ts,
            "importance": importance,
            "summary": summary or content[:60],
        }
        if metadata:
            meta.update(metadata)

        self._get_store().add(mem_id, content, meta)
        return mem_id

    # ── 读 ──

    def recall(
        self,
        query: str,
        *,
        agent_id: str = "",
        limit: int = 10,
        memory_types: Optional[list[str]] = None,
    ) -> list[dict]:
        """语义搜索跨会话记忆。

        Args:
            query: 搜索关键词/问题。
            agent_id: 限定 Agent（空=搜索所有 Agent）。
            limit: 最大结果数。
            memory_types: 限定记忆类型（如 ["decision", "insight"]）。

        Returns:
            [{id, content, score, agent_id, session_id, type, timestamp, importance, summary}, ...]
        """
        embedder = self._get_embedder()
        q_emb = embedder.embed(query)
        raw = self._get_store().query_by_embedding(q_emb, limit=limit * 2)

        if not raw or not raw.get("ids") or not raw["ids"][0]:
            return []

        results = []
        for i in range(len(raw["ids"][0])):
            meta = raw["metadatas"][0][i] if raw["metadatas"] else {}
            score = 1.0 / (1.0 + raw["distances"][0][i]) if raw.get("distances") else 0.0

            # Filter by agent_id
            if agent_id and meta.get("agent_id", "") != agent_id:
                continue

            # Filter by memory type
            if memory_types and meta.get("type", "") not in memory_types:
                continue

            results.append(
                {
                    "id": raw["ids"][0][i],
                    "content": raw["documents"][0][i] if raw.get("documents") else "",
                    "score": round(score, 4),
                    "agent_id": meta.get("agent_id", ""),
                    "session_id": meta.get("session_id", ""),
                    "type": meta.get("type", ""),
                    "timestamp": meta.get("timestamp", ""),
                    "importance": meta.get("importance", IMPORTANCE_NORMAL),
                    "summary": meta.get("summary", ""),
                }
            )

        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:limit]

    def get_session(self, agent_id: str, session_id: str) -> list[dict]:
        """获取某 Agent 某次会话的全部记忆（按时间正序）。"""
        # 用 session_id 和 agent_id 同时匹配作为查询
        query_text = f"session {session_id} agent {agent_id}"
        raw = self._get_store().query(query_text, limit=200)

        if not raw or not raw.get("ids") or not raw["ids"][0]:
            return []

        results = []
        for i in range(len(raw["ids"][0])):
            meta = raw["metadatas"][0][i] if raw["metadatas"] else {}
            if meta.get("agent_id") == agent_id and meta.get("session_id") == session_id:
                results.append(
                    {
                        "id": raw["ids"][0][i],
                        "content": raw["documents"][0][i] if raw.get("documents") else "",
                        "type": meta.get("type", ""),
                        "timestamp": meta.get("timestamp", ""),
                        "importance": meta.get("importance", IMPORTANCE_NORMAL),
                        "summary": meta.get("summary", ""),
                    }
                )

        results.sort(key=lambda r: r.get("timestamp", ""))
        return results

    def list_sessions(self, agent_id: str = "", limit: int = 50) -> list[dict]:
        """列出所有会话摘要（按最新时间倒序）。

        Args:
            agent_id: 限定 Agent（空=所有 Agent）。
            limit: 最大返回数。

        Returns:
            [{agent_id, session_id, count, last_timestamp, types}, ...]
        """
        # 拉取最近 entries 来构建会话列表
        raw = self._get_store().query("session memory", limit=min(limit * 3, 200))

        if not raw or not raw.get("ids") or not raw["ids"][0]:
            return []

        sessions: dict[str, dict] = {}
        for i in range(len(raw["ids"][0])):
            meta = raw["metadatas"][0][i] if raw["metadatas"] else {}
            a_id = meta.get("agent_id", "")
            s_id = meta.get("session_id", "")

            if not s_id:
                continue
            if agent_id and a_id != agent_id:
                continue

            key = f"{a_id}_{s_id}"
            if key not in sessions:
                sessions[key] = {
                    "agent_id": a_id,
                    "session_id": s_id,
                    "count": 0,
                    "last_timestamp": "",
                    "types": set(),
                }
            sessions[key]["count"] += 1
            ts = meta.get("timestamp", "")
            if ts > sessions[key]["last_timestamp"]:
                sessions[key]["last_timestamp"] = ts
            sessions[key]["types"].add(meta.get("type", ""))

        result = sorted(sessions.values(), key=lambda s: s["last_timestamp"], reverse=True)
        for s in result:
            s["types"] = sorted(s["types"])
        return result[:limit]

    # ── 会话压缩摘要 ──

    def summarize_session(
        self,
        agent_id: str,
        session_id: str,
        summary_text: str = "",
    ) -> dict:
        """将某次会话的所有记忆压缩为一条摘要。

        原记忆保留，新增一条 type=summary 的条目关联到该会话。

        Args:
            agent_id: Agent 标识。
            session_id: 会话 ID。
            summary_text: 摘要内容（不传则自动截取前 200 字）。

        Returns:
            创建的摘要条目信息。
        """
        memories = self.get_session(agent_id, session_id)
        if not memories:
            return {"error": "Session not found"}

        # 自动生成摘要：拼接关键内容
        if not summary_text:
            parts = []
            for m in memories:
                if m["type"] in (TYPE_DECISION, TYPE_INSIGHT, TYPE_USER_PREFERENCE):
                    parts.append(f"[{m['type']}] {m.get('summary', m['content'][:80])}")
            summary_text = "; ".join(parts) if parts else memories[-1]["content"][:200]

        mem_id = self.save(
            content=summary_text,
            agent_id=agent_id,
            session_id=session_id,
            memory_type=TYPE_SUMMARY,
            importance=IMPORTANCE_HIGH,
            summary=f"会话摘要: {session_id}",
        )

        return {
            "id": mem_id,
            "agent_id": agent_id,
            "session_id": session_id,
            "memory_count": len(memories),
            "summary": summary_text[:200],
        }

    # ── 删除 ──

    def delete_session(self, agent_id: str, session_id: str) -> int:
        """删除某次会话的全部记忆。"""
        memories = self.get_session(agent_id, session_id)
        if not memories:
            return 0
        for m in memories:
            try:
                self._get_store().delete(m["id"])
            except Exception as e:
                logger.warning("Failed to delete memory: %s", e)
        return len(memories)


# ── 单例 ──

_session_memory: Optional[SessionMemory] = None


def get_session_memory() -> SessionMemory:
    global _session_memory
    if _session_memory is None:
        _session_memory = SessionMemory()
    return _session_memory
