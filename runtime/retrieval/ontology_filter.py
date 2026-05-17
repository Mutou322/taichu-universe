"""本体过滤器 — 按分类标签过滤检索结果，防止图谱爆炸"""


def filter_by_ontology(docs: list[dict], allowed_categories: list[str] | None = None) -> list[dict]:
    """
    按层级过滤，防止图谱爆炸。

    当 allowed_categories 为空列表或 None 时，不过滤，原样返回。
    Phase 3 GBrain ontology_builder 稳定后启用。
    """
    if not allowed_categories:
        return docs

    filtered = []
    for doc in docs:
        category = doc.get("category") or doc.get("metadata", {}).get("category")
        if category and category in allowed_categories:
            filtered.append(doc)

    return filtered
