"""上下文构建器 — 将检索文档拼装为 Agent 可用的文本上下文"""

MAX_TOKENS = 2000


def build_context(docs: list[dict], max_tokens: int = MAX_TOKENS) -> str:
    """
    将检索结果组装成 Agent 可用的文本上下文。

    按 reask_score 降序取文档，直到 token 预算用完。
    """
    context_pieces = []
    token_count = 0

    for doc in docs:
        text = doc.get("text", "")
        tokens = max(1, len(text) // 4)  # 粗略估算：4 chars ≈ 1 token

        if token_count + tokens > max_tokens:
            break

        context_pieces.append(text)
        token_count += tokens

    return "\n\n---\n\n".join(context_pieces)
