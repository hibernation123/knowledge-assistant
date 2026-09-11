"""任务3-2：读取 kb_docs 文档，切分文本，并生成 SQLite 向量索引。"""

import json
import sqlite3
from contextlib import closing
from pathlib import Path

from ollama import embed


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "kb_docs"
DATABASE_PATH = BASE_DIR / "kb.db"
EMBEDDING_MODEL = "bge-m3"
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
SUPPORTED_SUFFIXES = {".md", ".txt"}


def split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    """把文本切成固定大小的片段，并在相邻片段之间保留少量重叠内容。"""

    if chunk_size <= 0:
        raise ValueError("chunk_size 必须大于 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap 必须大于等于 0，且小于 chunk_size")

    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - overlap

    return chunks


def embed_text(text: str):
    """使用 Ollama bge-m3 把一段文本转换成向量。"""

    response = embed(model=EMBEDDING_MODEL, input=text)
    return response.embeddings[0]


def build_index(docs_dir: Path, database_path: Path, embedder=embed_text):
    """处理文档并把文本片段和向量写入 SQLite。"""

    docs_dir = Path(docs_dir)
    database_path = Path(database_path)

    if not docs_dir.is_dir():
        raise FileNotFoundError(f"找不到知识库目录：{docs_dir}")

    document_paths = []

    for path in docs_dir.iterdir():
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            document_paths.append(path)

    document_paths = sorted(document_paths)

    if not document_paths:
        raise ValueError("kb_docs 目录中没有 .md 或 .txt 文档")

    records = []

    for document_path in document_paths:
        text = document_path.read_text(encoding="utf-8")

        for chunk_index, chunk in enumerate(split_text(text)):
            vector = embedder(chunk)
            records.append(
                (
                    document_path.name,
                    chunk_index,
                    chunk,
                    json.dumps(vector),
                )
            )

    if not records:
        raise ValueError("知识库文档为空，没有可建立索引的内容")

    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute("DROP TABLE IF EXISTS chunks")
            connection.execute(
                """
                CREATE TABLE chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embedding TEXT NOT NULL
                )
                """
            )
            connection.executemany(
                """
                INSERT INTO chunks (source, chunk_index, content, embedding)
                VALUES (?, ?, ?, ?)
                """,
                records,
            )

    return len(records)


def main():
    print(f"正在读取文档：{DOCS_DIR}")
    print(f"使用 Embedding 模型：{EMBEDDING_MODEL}")

    try:
        chunk_count = build_index(DOCS_DIR, DATABASE_PATH)
    except Exception as error:
        raise SystemExit(f"知识库构建失败：{error}") from error

    print(f"知识库构建完成，共生成 {chunk_count} 个文本片段。")
    print(f"索引数据库：{DATABASE_PATH}")


if __name__ == "__main__":
    main()
