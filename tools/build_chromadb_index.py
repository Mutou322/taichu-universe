#!/usr/bin/env python3
"""
方案B：ChromaDB 语义向量索引构建脚本
=====================================
为太初知识库的 wiki/ 文档构建语义搜索索引。

前置条件：
  pip install chromadb sentence-transformers

用法：
  python3 ~/taichu_knowledge/tools/build_chromadb_index.py          # 完整重建
  python3 ~/taichu_knowledge/tools/build_chromadb_index.py incremental  # 仅索引新文档
"""
import argparse
import sys
from pathlib import Path

VAULT = Path.home() / "taichu_knowledge"
WIKI_DIR = VAULT / "wiki"
DB_PATH = VAULT / "chroma_db"


def build_index():
    """构建 ChromaDB 向量索引（完整重建）"""
    # 尝试导入依赖
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        print(f"缺少依赖: {e}")
        print("请运行: pip install chromadb sentence-transformers")
        sys.exit(1)

    # 收集所有 .md 文件
    md_files = list(WIKI_DIR.rglob("*.md"))
    md_files = [f for f in md_files if f.stem != "index"]
    print(f"发现 {len(md_files)} 个 wiki 文档")

    if not md_files:
        print("没有文档需要索引")
        return

    # 加载轻量中文语义模型
    print("加载语义模型 (paraphrase-multilingual-MiniLM-L12-v2)...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    # 连接 ChromaDB（持久化）
    client = chromadb.PersistentClient(path=str(DB_PATH))
    # 如果已存在则重建（索引与文件系统同步）
    try:
        client.delete_collection("kb_articles")
    except Exception:
        pass
    collection = client.create_collection(name="kb_articles")

    # 逐条向量化
    batch_size = 50
    total = len(md_files)

    for i in range(0, total, batch_size):
        batch = md_files[i : i + batch_size]
        ids, documents, metadatas = [], [], []

        for f in batch:
            content = f.read_text(encoding="utf-8")
            # 取前 1000 字作为向量文本（全文太长会稀释语义）
            text_for_embed = content[:1000]
            # 用相对路径作唯一 ID（避免不同目录下同名文件冲突）
            rel_path = str(f.relative_to(WIKI_DIR))
            doc_id = rel_path.replace("/", "--").replace(".md", "")
            ids.append(doc_id)
            documents.append(content)
            metadatas.append({"source": f.name, "path": rel_path, "size": len(content)})

        # 批量编码
        embeddings = model.encode(documents, show_progress_bar=True).tolist()
        collection.add(embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids)
        print(f"  进度: {min(i+batch_size, total)}/{total}")

    print(f"\n✅ 索引完成: {collection.count()} 个词条")
    print(f"   数据库路径: {DB_PATH}")
    print(f"   模型: paraphrase-multilingual-MiniLM-L12-v2")
    print(f"   维度: {len(embeddings[0]) if embeddings else 'N/A'}")


def incremental_update():
    """增量索引：只索引不在 ChromaDB 中的新文档"""
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        print(f"缺少依赖: {e}")
        print("请运行: pip install chromadb sentence-transformers")
        sys.exit(1)

    # 收集所有 .md 文件
    md_files = list(WIKI_DIR.rglob("*.md"))
    md_files = [f for f in md_files if f.stem != "index"]
    total = len(md_files)
    print(f"总文档数: {total}")

    if not md_files:
        print("没有文档需要索引")
        return

    # 连接 ChromaDB
    client = chromadb.PersistentClient(path=str(DB_PATH))
    try:
        collection = client.get_collection(name="kb_articles")
    except Exception:
        print("ChromaDB 集合不存在，执行完整重建...")
        build_index()
        return

    existing_count = collection.count()
    print(f"ChromaDB 现有: {existing_count} 个词条")

    # 获取已有 ID 集合
    existing_ids = set()
    try:
        # ChromaDB get() with limit much larger than count returns all
        existing_data = collection.get(limit=existing_count + 100)
        if existing_data and existing_data.get("ids"):
            existing_ids = set(existing_data["ids"])
    except Exception:
        pass

    # 找出新文档
    new_files = []
    for f in md_files:
        rel_path = str(f.relative_to(WIKI_DIR))
        doc_id = rel_path.replace("/", "--").replace(".md", "")
        if doc_id not in existing_ids:
            new_files.append(f)

    if not new_files:
        print("✅ 没有新文档需要索引")
        return

    print(f"待索引新文档: {len(new_files)} 篇")

    # 编码并添加
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    batch_size = 50
    for i in range(0, len(new_files), batch_size):
        batch = new_files[i : i + batch_size]
        ids, documents, metadatas = [], [], []

        for f in batch:
            content = f.read_text(encoding="utf-8")
            rel_path = str(f.relative_to(WIKI_DIR))
            doc_id = rel_path.replace("/", "--").replace(".md", "")
            ids.append(doc_id)
            documents.append(content)
            metadatas.append(
                {
                    "source": f.name,
                    "path": rel_path,
                    "size": len(content),
                }
            )

        embeddings = model.encode(documents, show_progress_bar=True).tolist()
        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )
        print(f"  进度: {min(i+batch_size, len(new_files))}/{len(new_files)}")

    print(f"\n✅ 增量索引完成: 新增 {len(new_files)} 个词条")
    print(f"   数据库路径: {DB_PATH}")
    print(f"   模型: paraphrase-multilingual-MiniLM-L12-v2")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ChromaDB semantic index builder")
    parser.add_argument(
        "mode",
        nargs="?",
        default="full",
        choices=["full", "incremental"],
        help="'full': complete rebuild; 'incremental': only index new docs",
    )
    args = parser.parse_args()
    if args.mode == "incremental":
        incremental_update()
    else:
        build_index()
