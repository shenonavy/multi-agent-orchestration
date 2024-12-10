from typing import List, Dict, Any, Optional, Type
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from langchain.schema import Document
from langchain.vectorstores.base import VectorStore
from langchain.embeddings.base import Embeddings
from langchain.schema.retriever import BaseRetriever
from pydantic import Field
import numpy as np
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class DocumentVector(Base):
    __tablename__ = 'document_vectors'

    id = Column(Integer, primary_key=True)
    content = Column(String)
    doc_metadata = Column(JSON)  # Renamed from metadata to doc_metadata
    embedding = Column(Vector(1536))  # OpenAI embeddings are 1536 dimensions

class CustomPGVector(VectorStore):
    def __init__(
        self,
        connection_string: str,
        embedding_function: Embeddings,
        collection_name: str = "document_vectors"
    ):
        self.embedding_function = embedding_function
        self.engine = create_engine(connection_string)
        Base.metadata.create_all(self.engine)
        self.collection_name = collection_name

    @classmethod
    def from_texts(
        cls: Type[VectorStore],
        texts: List[str],
        embedding: Embeddings,
        metadatas: Optional[List[dict]] = None,
        connection_string: str = "",
        collection_name: str = "document_vectors",
        **kwargs: Any,
    ) -> "CustomPGVector":
        """Create a CustomPGVector instance from texts."""
        store = cls(
            connection_string=connection_string,
            embedding_function=embedding,
            collection_name=collection_name,
        )
        store.add_texts(texts, metadatas, **kwargs)
        return store

    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """Add texts to the vector store."""
        embeddings = self.embedding_function.embed_documents(texts)
        
        with Session(self.engine) as session:
            doc_vectors = []
            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                metadata = metadatas[i] if metadatas else {}
                doc_vector = DocumentVector(
                    content=text,
                    doc_metadata=metadata,  # Using renamed column
                    embedding=embedding
                )
                doc_vectors.append(doc_vector)
            
            session.add_all(doc_vectors)
            session.commit()
            
            return [str(dv.id) for dv in doc_vectors]

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        **kwargs: Any,
    ) -> List[Document]:
        """Return docs most similar to query."""
        embedding = self.embedding_function.embed_query(query)
        
        with Session(self.engine) as session:
            # Using pgvector's L2 distance operator <->
            results = session.query(DocumentVector).order_by(
                DocumentVector.embedding.l2_distance(embedding)
            ).limit(k).all()
            
            return [
                Document(
                    page_content=result.content,
                    metadata=result.doc_metadata  # Using renamed column
                )
                for result in results
            ]

    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store."""
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        return self.add_texts(texts, metadatas)

    async def aadd_documents(self, documents: List[Document]) -> List[str]:
        """Async add documents to the vector store."""
        return self.add_documents(documents)

    def as_retriever(self, **kwargs: Any):
        """Return a retriever interface for the vector store."""
        return CustomRetriever(vectorstore=self, search_kwargs=kwargs)

class CustomRetriever(BaseRetriever):
    vectorstore: CustomPGVector = Field(description="Vector store for document retrieval")
    search_kwargs: dict = Field(default_factory=dict, description="Search parameters")

    def _get_relevant_documents(self, query: str, **kwargs):
        search_kwargs = {**self.search_kwargs, **kwargs}
        return self.vectorstore.similarity_search(query, **search_kwargs)
    
    async def _aget_relevant_documents(self, query: str, **kwargs):
        return self._get_relevant_documents(query, **kwargs)
