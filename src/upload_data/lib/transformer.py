# import uuid TODO: replace int to uuid in code
from typing import List
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


def split_docs(docs: List[Document]) -> List[Document]:
    # Markdown
    headers_to_split_on = [
        ("#", "Titre 1"),
        ("##", "Sous-titre 1"),
        ("###", "Sous-titre 2"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    # Split based on markdown and add original metadata
    md_docs = []
    for doc in docs:
        md_doc = markdown_splitter.split_text(doc.page_content)
        for i in range(len(md_doc)):
            md_doc[i].metadata = md_doc[i].metadata | doc.metadata
        md_docs.extend(md_doc)

    # Chunk size big enough
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=20,
        separators=["\n\n", "\n", "(?<=\. )", " ", ""]  # noqa
    )

    splitted_docs = splitter.split_documents(md_docs)

    return splitted_docs
