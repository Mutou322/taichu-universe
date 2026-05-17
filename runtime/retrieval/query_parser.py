"""查询解析器 — 将自然语言查询解析为结构化的 topic/relation/concept/intent 字典"""

import re


def parse_query(query: str) -> dict:
    """
    把用户输入解析成标准化 query dict。

    Example:
    "transformer 为什么 attention collapse"
    => {"topic": "transformer", "relation": "causes", "concept": "attention collapse", "intent": "explanation"}
    """
    result = {
        "topic": None,
        "relation": None,
        "concept": None,
        "intent": None,
        "raw": query,
    }

    if "为什么" in query:
        result["relation"] = "causes"
        parts = query.split("为什么", 1)
        result["topic"] = parts[0].strip()
        result["concept"] = parts[1].strip() if len(parts) > 1 else ""
        result["intent"] = "explanation"
    elif "如何" in query or "怎么" in query:
        result["relation"] = "method"
        parts = re.split(r"如何|怎么", query, maxsplit=1)
        result["topic"] = parts[0].strip()
        result["concept"] = parts[1].strip() if len(parts) > 1 else ""
        result["intent"] = "instruction"
    elif "对比" in query or "区别" in query:
        result["relation"] = "comparison"
        result["topic"] = query
        result["intent"] = "comparison"
    else:
        result["topic"] = query
        result["concept"] = query
        result["intent"] = "search"

    return result
