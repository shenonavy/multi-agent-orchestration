from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from app.utils.logger import logger
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.utils.vector_store import CustomPGVector
from langchain.docstore.document import Document

class KnowledgeAgent:
    def __init__(self, connection_string: str, openai_api_key: str):
        self.llm = ChatOpenAI(
            temperature=0,
            model_name="gpt-4o-mini",
            openai_api_key=openai_api_key
        )
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        
        # Initialize custom PGVector store
        self.vectorstore = CustomPGVector(
            connection_string=connection_string,
            embedding_function=self.embeddings,
            collection_name="insurance_docs"
        )
        
        template = """You are an insurance customer service AI assistant. Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        {context}
        
        Question: {question}
        Answer: """
        
        QA_PROMPT = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        self.qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(),
            chain_type_kwargs={"prompt": QA_PROMPT}
        )

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run the knowledge agent and determine next steps"""
        logger.debug(f"KnowledgeAgent processing query: {state.query}")
        
        # Check if we should use API first
        keywords = ["status", "update", "submit", "claim", "policy", "account"]
        if any(keyword in state.query.lower() for keyword in keywords):
            # Skip knowledge search for API-related queries
            logger.debug("Query contains API keywords, skipping knowledge search")
            state.knowledge_found = False
            return state

        query = state.query
        try:
            # Try to get answer from knowledge base
            response = self.qa.invoke({"query": state.query})
            answer = response["result"] if isinstance(response, dict) else str(response)
            
            if answer and len(str(answer).strip()) > 0:
                logger.debug("Found answer in knowledge base")
                state.knowledge_found = True
                state.knowledge_response = str(answer)
            else:
                logger.debug("No answer found in knowledge base")
                state.knowledge_found = False
                state.knowledge_response = None
        except Exception as e:
            logger.error(f"Error querying knowledge base: {e}")
            state.knowledge_found = False
            state.knowledge_response = None
        
        return state

    async def process_and_store_document(self, file_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a document and store its contents as vectors in the database."""
        try:
            logger.debug(f"Processing document: {file_path}")
            # Load document based on file type
            if file_path.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
                documents = loader.load()
            elif file_path.endswith(('.docx', '.doc')):
                loader = Docx2txtLoader(file_path)
                documents = loader.load()
            elif file_path.endswith('.txt'):
                loader = TextLoader(file_path)
                documents = loader.load()
            else:
                raise ValueError("Unsupported file type. Only PDF, Word documents, and text files are supported.")

            logger.debug(f"Loaded document with {len(documents)} pages/sections")
            
            # Split the document into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            splits = text_splitter.split_documents(documents)
            logger.debug(f"Split document into {len(splits)} chunks")

            # Add metadata to each split if provided
            if metadata:
                for split in splits:
                    split.metadata.update(metadata)
            
            # Store document chunks in vector store
            logger.debug("Storing document chunks in vector store")
            self.vectorstore.add_documents(splits)
            
            result = {
                "status": "success",
                "message": "Document processed and stored successfully",
                "document_id": metadata.get("policy_number") if metadata else None,
                "chunks": len(splits)
            }
            logger.info(f"Document processing completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}", exc_info=True)
            raise Exception(f"Error processing document: {str(e)}")

    async def query(self, question: str) -> Dict[str, Any]:
        try:
            response = await self.qa.ainvoke({"query": question})
            return {
                "answer": response["result"],
                "source_documents": response.get("source_documents", [])
            }
        except Exception as e:
            logger.error(f"Error querying knowledge base: {str(e)}")
            return {
                "error": str(e),
                "answer": "I apologize, but I encountered an error while searching the knowledge base."
            }
