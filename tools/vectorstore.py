import os
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

POLICY_FILES = [
    "data/returns_policy.md",
    "data/warranty_policy.md",
    "data/shipping_policy.md",
]

PERSIST_DIR = "vectorstore/chroma_db"

TABLE_BLOCK_RE = re.compile(r"((?:^\|.*\|\s*\n)+)", re.MULTILINE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)


def extract_sections_with_tables(text: str):
    """
    Splits text into ordered blocks, keeping each markdown table as one
    atomic block (prefixed with its nearest preceding heading for context),
    and everything else as separate prose blocks.
    """
    blocks = []
    last_heading = ""
    pos = 0

    # walk through text, tracking the most recent heading as we go
    for match in re.finditer(r"(^#{1,6}\s+.*$)|((?:^\|.*\|\s*$\n?)+)", text, re.MULTILINE):
        start, end = match.span()

        # prose between previous position and this match
        if start > pos:
            prose = text[pos:start].strip()
            if prose:
                blocks.append(("prose", last_heading, prose))

        matched_text = match.group(0)

        if matched_text.lstrip().startswith("|"):
            # it's a table block — attach last heading as context
            blocks.append(("table", last_heading, matched_text.strip()))
        else:
            # it's a heading line — update tracker, also keep as prose marker
            last_heading = matched_text.strip()

        pos = end

    # trailing prose after the last match
    if pos < len(text):
        trailing = text[pos:].strip()
        if trailing:
            blocks.append(("prose", last_heading, trailing))

    return blocks


def build_vector_store():
    all_chunks = []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "]
    )

    for filepath in POLICY_FILES:
        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()

        source_name = os.path.basename(filepath)
        blocks = extract_sections_with_tables(raw_text)

        for block_type, heading, content in blocks:
            if block_type == "table":
                # keep table whole, just attach heading as context, no further splitting
                full_text = f"{heading}\n{content}" if heading else content
                all_chunks.append(Document(
                    page_content=full_text,
                    metadata={"source_file": source_name, "block_type": "table"}
                ))
            else:
                # prose can still be split normally if long
                sub_docs = splitter.split_documents([
                    Document(page_content=content, metadata={"source_file": source_name, "block_type": "prose"})
                ])
                for d in sub_docs:
                    if heading:
                        d.page_content = f"{heading}\n{d.page_content}"
                all_chunks.extend(sub_docs)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vectordb = Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR
    )

    print(f"Stored {len(all_chunks)} chunks into ChromaDB at {PERSIST_DIR}")
    return vectordb


def load_vector_store():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)


if __name__ == "__main__":
    build_vector_store()