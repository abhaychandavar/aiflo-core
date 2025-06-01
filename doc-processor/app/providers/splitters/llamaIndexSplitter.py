
from llama_index.core.node_parser import (
    SentenceSplitter,
    SemanticSplitterNodeParser,
)
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import TokenTextSplitter
from typing import List, Sequence
from app.types.textDocument import TextDocument
from llama_index.core import Document

class LLAMAIndexSemanticSplitter:
    def __init__(self, max_characters):
        embed_model = OpenAIEmbedding()
        self.max_characters = max_characters
        self.splitter = SemanticSplitterNodeParser(
            buffer_size=5, 
            breakpoint_percentile_threshold=95, 
            embed_model=embed_model, 
            include_metadata=True,
            include_prev_next_rel=True
        )
        self.token_splitter = TokenTextSplitter(
            chunk_size=max_characters,
            chunk_overlap=20,
            separator=" "
        )
    
    def split_semantically(self, documents: Sequence[Document]):
        semantic_nodes = self.splitter.get_nodes_from_documents(documents)
    
        final_nodes = []
        for node in semantic_nodes:
            if len(node.text) > self.max_characters:
                sub_nodes = self.token_splitter.get_nodes_from_documents([node])
                final_nodes.extend(sub_nodes)
            else:
                final_nodes.append(node)

        text_documents: List[TextDocument] = []
        for node in final_nodes:
            doc: TextDocument = {
                "id": node.node_id,
                "text": node.text,
                "metadata": node.metadata,
                "relationships": node.relationships,
            }
            text_documents.append(doc)

        return text_documents
    
    def parse_documents(self, text_documents: List[TextDocument]) -> Sequence[Document]:
        documents: Sequence[Document] = []
        for text_document in text_documents:
            document =  Document(
                            text=text_document["text"],
                            metadata=text_document["metadata"]
                        )
            documents.append(document)
        return documents

            
            
