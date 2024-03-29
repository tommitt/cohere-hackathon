import os

import pinecone
from langchain.vectorstores import VectorStore
from langchain_community.embeddings import CohereEmbeddings
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.vectorstores.pinecone import Pinecone
from langchain_core.documents import Document

from app.constants import (
    CHROMA_FOLDER,
    COHERE_API_KEY,
    COHERE_EMBEDDING_MODEL,
    PINECONE_API_KEY,
    PINECONE_INDEX,
    USE_LOCAL_VECTORSTORE,
)
from app.db import DataframeORM, ValueORM, VariableORM
from app.db.models import UnstructuredORM


def get_live_vectorstore() -> VectorStore:
    pc = pinecone.Pinecone(PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX)

    return Pinecone(
        index=index,
        embedding=CohereEmbeddings(
            cohere_api_key=COHERE_API_KEY, model=COHERE_EMBEDDING_MODEL
        ),
        text_key="text",
    )


def get_local_vectorstore() -> Chroma:
    if not os.path.exists(CHROMA_FOLDER):
        os.makedirs(CHROMA_FOLDER)

    return Chroma(
        persist_directory=CHROMA_FOLDER,
        embedding_function=CohereEmbeddings(
            cohere_api_key=COHERE_API_KEY, model=COHERE_EMBEDDING_MODEL
        ),
    )


def get_vectorstore() -> VectorStore:
    if USE_LOCAL_VECTORSTORE:
        return get_local_vectorstore()
    return get_live_vectorstore()


def orm_to_vectorstore(orm: DataframeORM | VariableORM | ValueORM) -> str:
    """Add a SQL object to the vectorstore"""
    vectorstore = get_vectorstore()

    page_content = f"{orm.name}\n{orm.description}"
    doc = Document(
        page_content=page_content,
        metadata={"id": orm.id, "type": type(orm).__name__},
    )

    res = vectorstore.add_documents([doc])
    return res[0]


def unstructured_orm_to_vectorstore(orm: UnstructuredORM) -> str:
    """Add a SQL UnstructuredORM object to the vectorstore"""
    vectorstore = get_vectorstore()

    page_content = f"{orm.name}\n{orm.description}\n{orm.content}"
    doc = Document(
        page_content=page_content,
        metadata={"id": orm.id, "type": type(orm).__name__},
    )

    res = vectorstore.add_documents([doc])
    return res[0]


def doc_to_vectorstore(doc_in: dict[str, str]) -> str:
    """
    Add a document to the vectorstore.
    The document is a dictionary with any number of key and value pairs - it must contain the "id" and "type" keys.
    """
    vectorstore = get_vectorstore()

    page_content = "\n".join([f"{k}: {v}" for k, v in doc_in.items()])
    doc = Document(
        page_content=page_content,
        metadata={"id": doc_in["id"], "type": doc_in["type"]},
    )

    res = vectorstore.add_documents([doc])
    return res[0]
