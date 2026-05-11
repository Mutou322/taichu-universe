from pathlib import Path
from .types import IngestResult

from core.vision.doubao_vision import vision_analyze

VISION_PROMPT = """
请分析这张图片中的内容。

要求：
1. 提取所有可见文字
2. 识别 UI 布局和界面结构
3. 总结界面功能
4. 如果是知识图谱/终端/代码界面，请描述结构
5. 输出为结构化 Markdown
"""


def ingest_image(path: Path) -> IngestResult:
    result = vision_analyze(
        image_path=str(path),
        prompt=VISION_PROMPT,
    )

    return IngestResult(
        text=result,
        modality="image",
        metadata={
            "source": str(path),
            "type": "image",
            "ext": path.suffix.lower(),
        },
    )
