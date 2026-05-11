# 太初知识宇宙架构

## 设计初衷
构建一个可进化的个人知识操作系统，超越文件堆，实现语义理解、自动关联与实时运行。

## 五层职责
1. **摄取层 (ingest)** — 多模态文件 → 纯文本 Markdown
2. **语义层 (knowledge)** — 词条、双链、关系图谱
3. **存储层 (storage)** — 向量索引、嵌入、快照
4. **运行时 (runtime)** — 记忆推理、事件总线、Agent 调度
5. **协议层 (protocols)** — 统一数据 Schema

## 关键约束
- 严禁跨层直接访问（如 UI 读 ChromaDB）
- 所有路径通过 config/paths.yaml 配置
- 语义层不依赖存储层具体实现

## 数据流
用户操作 → ingest → raw/ → compile → wiki/ → graph builder → ChromaStore → runtime Agent
