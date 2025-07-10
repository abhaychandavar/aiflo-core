from app.nodes.interfaces.baseNodeProvider import BaseNode
from app.nodes.types.nodeTypes import NodeType
from app.nodes.services.result.default import DefaultResultNode
from app.nodes.interfaces.baseNodeService import Node
from app.nodes.types.nodeTypes import ExecutionResultType, NodeServiceExecutionResultType
from app.config.knowledgeBase import KNOWLEDGE_BASE
from app.nodes.services.knowledgeBase.quadrant import QUADRANT
from typing import AsyncGenerator
from app.providers.embeddings.openAIEmbeddings import OpenAIEmbeddings
from app.providers.embeddings.fastEmbedEmbeddings import FastEmbeddings
from app.services.embeddings import Embeddings
from app.nodes.state.nodeExecState import NodeExecState

class KnowledgeBase(BaseNode):
    def __init__(self, id: str, incoming_nodes: dict, config: dict, node_exec_state_instance: NodeExecState):
        self.id = id
        self.type: NodeType = "knowledgeBase"
        self.config: dict = config
        self.incoming_nodes = incoming_nodes
        self.node_exec_state_instance = node_exec_state_instance

        super().__init__()

    def __get_node_service(self):
        db = self.config.get("vectorDb")
        if not db:
            db = KNOWLEDGE_BASE.QUADRANT["id"]
        switcher: dict[KNOWLEDGE_BASE, any] = {
            KNOWLEDGE_BASE.QUADRANT["id"]: QUADRANT
        }
        return switcher[db]
    
    async def execute(self, data: ExecutionResultType) -> ExecutionResultType:
        node_instance = self.__get_node_service()
        if not node_instance:
            res = {
                "error": "Knowledge base vector database not configured",
                "errorCode": f"{self.type}/execute/model_not_configured",
                "nodeID": self.id,
                "nodeType": self.type,
                "type": "error"
            }
            self.node_exec_state_instance.set_node_exec_res(res)
            return res
        
        top_results = self.config.get("topResults") or 10
        override_query = self.config.get("query")

        type = self.config.get("type") or "hybrid"
        openai_embeddings_provider = OpenAIEmbeddings()
        embeddings = Embeddings(provider=openai_embeddings_provider)

        fastembed_embeddings_provider = FastEmbeddings(model_name="prithivida/Splade_PP_en_v1")
        sparse_embeddings = Embeddings(provider=fastembed_embeddings_provider)

        content = data.get("data")
        query = override_query if override_query else content.get("text")

        if not query:
            res = {
                "error": "Input query is required",
                "errorCode": f"{self.type}/execute/query_required",
                "nodeID": self.id,
                "nodeType": self.type,
                "type": "error",
                "source": data.get("nodeID")
            }
            self.node_exec_state_instance.set_node_exec_res(res)
            return res
        
        node_instance = node_instance(
            top_results,
            query,
            type=type, 
            generate_dense_vectors=embeddings.embed, 
            generate_sparse_vectors=sparse_embeddings.embed,
            doc_ids=self.config.get("docIds")
        )
        
        res = node_instance.execute()
        res = {
            "nodeID": self.id,
            "data": res,
            "nodeType": self.type,
            "source": data.get("nodeID")
        }
        self.node_exec_state_instance.set_node_exec_res(res)
        return res
        
    