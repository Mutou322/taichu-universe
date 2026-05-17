#!/usr/bin/env python3
"""验证 ChromaDB 索引可查询"""
import os
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

_TAICHU_HOME = Path(os.environ.get("TAICHU_HOME", str(Path.home() / "taichu"))).expanduser().resolve()
DB_PATH = str(_TAICHU_HOME / "storage" / "vector" / "chroma")

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_collection(name="kb_articles")

print(f"集合文档数: {collection.count()}")

# 测试查询
query = "向量数据库 语义搜索"
q_emb = model.encode(query).tolist()
results = collection.query(query_embeddings=[q_emb], n_results=3)

print(f'\n查询: "{query}"')
print(f"返回 {len(results['ids'][0])} 条结果:\n")

for i in range(len(results["ids"][0])):
    doc_id = results["ids"][0][i]
    meta = results["metadatas"][0][i]
    doc = results["documents"][0][i][:200]
    dist = results["distances"][0][i]
    print(f"  [{i+1}] {doc_id}")
    print(f"      距离: {dist:.4f}")
    print(f"      来源: {meta['source']}")
    print(f"      路径: {meta['path']}")
    print(f"      大小: {meta['size']} 字节")
    print(f"      预览: {doc}...")
    print()

print("验证通过：索引可正常查询。")
