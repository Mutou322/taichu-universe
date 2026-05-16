"""
太初知识宇宙 — CI/CD 使用指南

## 安装

pre-commit install

## 本地运行测试

pytest tests/ -v              # 全部测试
pytest tests/ -m "not slow"   # 跳过慢测试

## pre-commit hooks（git commit 时自动运行）

配置在 .pre-commit-config.yaml，包含：
- trailing-whitespace: 去除行尾空格
- end-of-file-fixer: 文件末尾换行
- check-yaml: YAML 语法检查
- check-added-large-files: 大文件检查（>500KB）
- check-merge-conflict: 合并冲突检查
- detect-private-key: 私钥泄露检测
- black: Python 代码格式化（line-length=120）
- isort: import 排序
- flake8: Python 代码规范检查
- bandit: 安全扫描
- mypy: 类型检查

手动运行全部 hooks: pre-commit run --all-files

## 运行安全检查

bandit -c pyproject.toml -r .

## 代码格式化

black .
isort .

## 配置文件

- pyproject.toml: black/isort/pytest/mypy/coverage 配置
- .flake8: flake8 配置
- .pre-commit-config.yaml: pre-commit hooks 配置
"""
