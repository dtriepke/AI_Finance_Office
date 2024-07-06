import openai
import os
from pathlib import Path  
import urllib.parse
from typing import Optional
import requests
import pickle

os.environ["OPENAI_API_KEY"] ="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"
openai.api_key  = os.getenv('OPENAI_API_KEY')

# LlamaIndex
from llama_index.llms.openai import OpenAI
llm_gpt4 = OpenAI(temperature=0.1, model="gpt-4")
llm_gpt4_0613 = OpenAI(model_name="gpt-4-0613")
llm_gpt3_turbo_0125 = OpenAI(model_name="gpt-3.5-turbo-0125")

from llama_index.core import get_response_synthesizer
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.schema import Document
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.tools.tool_spec.base import BaseToolSpec
from llama_index.core.tools.tool_spec.load_and_search.base import LoadAndSearchToolSpec
from llama_index.core import VectorStoreIndex, SummaryIndex, SimpleDirectoryReader

from llama_index.core.objects import (
    ObjectIndex,
    SimpleToolNodeMapping,
    ObjectRetriever,
)

from llama_index.core.retrievers import BaseRetriever
from llama_index.legacy.postprocessor.cohere_rerank import CohereRerank
from llama_index.core.postprocessor import LLMRerank
from llama_index.core.postprocessor import SimilarityPostprocessor



from llama_index.core.agent import ReActAgent
from llama_index.agent.openai import OpenAIAgent


from .utils import create_index_from_db_with_DeepLakeVectorStore, create_index_from_file_with_DeepLakeVectorStore


import nest_asyncio
nest_asyncio.apply()

# For cut the name for llamaINdex name restriction 
def query_engine_name_checker(name):
    if len(name) >= 63:
        name = name[:62]
    return name

from llama_index.core import VectorStoreIndex, ServiceContext

# Define the directory path
directory_path = ".\\data\\ifrs\\"

# List to hold all found PDF files
pdf_files = []

# Build agents dictionary
agents_dict = {}
extra_info_dict = {}

service_context = ServiceContext.from_defaults(llm=llm_gpt3_turbo_0125)

def get_sub_agents():

    def build_agent_per_document(file_base, file_path, load_index_from_deeplake = True):

        # Read pdf file and transform into text documents per page
        print(file_path)
        reader = SimpleDirectoryReader(input_files=[file_path])
        documents = reader.load_data()

        # INDEX:
        print ("Get Index for", file_base)
        if load_index_from_deeplake:
            vector_index = create_index_from_db_with_DeepLakeVectorStore("dennistriepke", file_base)
            summary_index = SummaryIndex(documents, service_context=service_context)
        else: 
            vector_index = create_index_from_file_with_DeepLakeVectorStore(documents, "dennistriepke", file_base, overwrite = True) # Just for the first time from documents
            summary_index = SummaryIndex(documents, service_context=service_context)
        
        # define query engines
        vector_query_engine = vector_index.as_query_engine()
        summary_query_engine = summary_index.as_query_engine(response_mode="tree_summarize")

        # Extract a summary from all documents for describing the summary query engine
        summary_out_path = f"./data/ifrs/llamaindex_docs/{file_base}_summary.pkl"
        if not os.path.exists(summary_out_path):
            Path(summary_out_path).parent.mkdir(parents=True, exist_ok=True)
            summary = str(summary_query_engine.query("Extract a concise 1-2 line summary of this document").response)
            pickle.dump(summary, open(summary_out_path, "wb"))
        else:
            summary = pickle.load(open(summary_out_path, "rb"))


        # define tools
        query_engine_tools = [
            QueryEngineTool(
                query_engine=vector_query_engine,
                metadata=ToolMetadata(
                    name= query_engine_name_checker(f"vector_tool_{file_base}"),
                    description=f"Useful for questions related to specific facts",
                ),
            ),
            QueryEngineTool(
                query_engine=summary_query_engine,
                metadata=ToolMetadata(
                    name= query_engine_name_checker(f"summary_tool_{file_base}"),
                    description=f"Useful for summarization questions",
                ),
            ),
        ]

        # build agent
        # function_llm = OpenAI(model="gpt-4")
        function_llm = OpenAI(model_name="gpt-3.5-turbo-0125")
        agent = OpenAIAgent.from_tools(
            query_engine_tools,
            llm=function_llm,
            verbose=True,
            system_prompt=f"""\
        You are a specialized agent designed to answer queries about the `{file_base}` part of the IFRS docs.
        You must ALWAYS use at least one of the tools provided when answering a question; do NOT rely on prior knowledge.

        **Ruls for the tool selection**
        - summary_tool_{file_base}: use this tool first to plan your task and summarizaiton issues 
        - vector_tool_{file_base}: use for task solving and detailed information extraxtion
        """,
        )
        return agent, summary

    # Walk through the directory
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            # Check if the file is a PDF by its extension
            if file.lower().endswith(".pdf"):

                # Construct full file path and add it to the list
                file_path = os.path.join(root, file)
                pdf_files.append(file_path)

                # Get filename 
                file_base = file.replace("r'^[a-zA-Z0-9\-_]+$'","_").replace(".", "_")
                print("\n\n", file_base)

                agent, summary = build_agent_per_document(file_base, file_path,  load_index_from_deeplake = True)

                print("Add agent to dict:", file_path)
                agents_dict[file_base] = agent
                extra_info_dict[file_base] = {"summary": summary}

    return agents_dict, extra_info_dict

def transform_agent_to_tool(agents_dict, extra_info_dict):
    # define tool for each document agent
    all_tools = []
    for file_base, agent in agents_dict.items():
        print("Define Agent Tool:", file_base)
        summary = extra_info_dict[file_base]["summary"]
        
        doc_tool = QueryEngineTool(
            query_engine=agent,
            metadata=ToolMetadata(
                name= query_engine_name_checker(f"tool_{file_base}").replace("-", "_"),
                description=summary,
            ),
        )

        all_tools.append(doc_tool)


    for t in all_tools:
        print(t.metadata.name)
    # print(all_tools[0].metadata)

    return all_tools


# define an "object" index and retriever over these tools
# define a custom retriever with reranking
class CustomRetriever(BaseRetriever):
    """
    A custom retriever class that extends the BaseRetriever for retrieving nodes based on vector similarity.
    It incorporates a postprocessing step to rerank the retrieved nodes.
    
    Attributes:
        _vector_retriever: The vector-based node retriever.
        _postprocessor: The postprocessing component for reranking the nodes.
    """

    def __init__(self, vector_retriever, postprocessor=None):
        """
        Initializes the CustomRetriever with a vector retriever and an optional postprocessor.
        
        Parameters:
            vector_retriever: The vector-based node retriever.
            postprocessor: An optional postprocessor for reranking. Defaults to CohereRerank if not provided.
        """

        self._vector_retriever = vector_retriever
        self._postprocessor = postprocessor or CohereRerank(top_n=10, api_key="COHERE_API_KEY")
        super().__init__()

    def _retrieve(self, query_bundle):
        """
        Retrieves and postprocesses nodes based on the provided query bundle.
        
        Parameters:
            query_bundle: The query information package used for retrieval.
        
        Returns:
            A list of filtered and reranked nodes.
        """
        retrieved_nodes = self._vector_retriever.retrieve(query_bundle)
        filtered_nodes = self._postprocessor.postprocess_nodes(retrieved_nodes, query_bundle=query_bundle)

        return filtered_nodes

# This class incorporates additional logic for query planning using retrieved tools.
class CustomObjectRetriever(ObjectRetriever):
    """
    A custom object retriever that utilizes a custom retrieval logic along with query planning.

    Attributes:
    retriever (CustomRetriever): The custom retriever for initial retrieval.
    object_node_mapping (SimpleToolNodeMapping): Mapping between objects and nodes.
    llm (OpenAI): An instance of the OpenAI model for processing.
    """

    def __init__(self, retriever, object_node_mapping, all_tools, llm=None):
        """
        Initializes the CustomObjectRetriever with a retriever, mapping, and optionally an LLM.

        Parameters:
        retriever (CustomRetriever): The custom retriever used for initial retrieval.
        object_node_mapping (SimpleToolNodeMapping): The mapping between objects and their corresponding nodes.
        all_tools: A collection of all tools available for retrieval.
        llm (OpenAI, optional): The Large Language Model instance. Defaults to a new OpenAI instance.
        """
        self._retriever = retriever
        self._object_node_mapping = object_node_mapping
        self._llm = llm or OpenAI("gpt-4-0613")

    def retrieve(self, query_bundle):
        """
        Retrieves relevant tools based on the provided query bundle.

        Parameters:
        query_bundle: The query data used for tool retrieval.

        Returns:
        A list of tools relevant to the query, enhanced with a query planning tool.
        """
        # Retrieve the tool nodes from query
        nodes = self._retriever.retrieve(query_bundle)
        
        # Get the query engine tools object from retrieved node
        tools = [self._object_node_mapping.from_node(n.node) for n in nodes]

        return tools
#         # Initialize a query engine for sub-questions with the retrieved tools.
#         sub_question_sc = ServiceContext.from_defaults(llm=self._llm)
#         sub_question_engine = SubQuestionQueryEngine.from_defaults(query_engine_tools=tools, service_context=sub_question_sc, verbose=True)
        
#         # Create a QueryEngineTool specifically designed for comparison queries.
#         sub_question_tool = QueryEngineTool(
#             query_engine=sub_question_engine,
#             metadata=ToolMetadata(
#                 name="compare_tool", 
#                 description=f"""\
# Useful for any queries that involve comparing multiple documents. ALWAYS use this tool for comparison queries - make sure to call this \
# tool with the original query. Do NOT use the other tools for any queries involving multiple documents.
# """
#             ),
#         )

#         return tools + [sub_question_tool]
    
# CUSTOM NODE RETRIEVER
def build_custom_object_retreiver():

    # Build or load per document one agent 
    agents_dict, extra_info_dict = get_sub_agents()
    
    # Transform the agents into query tools 
    all_tools = transform_agent_to_tool(agents_dict, extra_info_dict)

    # Create a tool-node mapping from a list of tools. This mapping aids in managing the association between tools and their corresponding nodes.
    tool_mapping = SimpleToolNodeMapping.from_objects(all_tools)

    # Instantiate an ObjectIndex for indexing and retrieving tool objects, leveraging a VectorStoreIndex for vector-based operations.
    obj_index = ObjectIndex.from_objects(all_tools, tool_mapping, VectorStoreIndex)

    # Establish a node retriever based on vector similarity, specifying the number of top similar nodes to be retrieved.
    vector_node_retriever = obj_index.as_node_retriever(similarity_top_k=10)

    # Custom Retriever
    custom_node_retriever = CustomRetriever(vector_node_retriever, postprocessor = LLMRerank(top_n=10, service_context=service_context))

    #CUSTOM OBJECT RETREIVER FROM NODE
    # Wrap the custom object retriever to handle query engine tools retrieval, effectively integrating query planning.
    custom_obj_retriever = CustomObjectRetriever(custom_node_retriever, tool_mapping, all_tools, llm=llm_gpt3_turbo_0125)

    return custom_obj_retriever


def ifrs_react_agent():

    # Custom object retreiver
    custom_obj_retriever = build_custom_object_retreiver()

    ifrs_agent = ReActAgent.from_tools(
        tool_retriever=custom_obj_retriever,
        system_prompt=""" \
    You are an agent designed to answer queries about the IFRS accounting standards documentation.
    Plan which tools to use in order to retrieve accounting standard information needed based on the user query. 
    You can choose if you require a tool for your answer. 

    #  Steps for Transaction Input Analysis
    1. **Capture Transaction Details**: Collects detailed information about each transaction, including the date, amounts, accounts involved, and a description of the transaction.  
    2. **Contextual Information**: Next determine context-specific information that might affect IFRS compliance, such as the nature of the transaction (e.g., lease, revenue recognition, financial instrument), the involved parties, and any contractual terms.  
    3. **IFRS Rule Mapping**: Map the captured transaction details to relevant IFRS rules. This involves recognizing the transaction type and determining the applicable standards (e.g., IFRS 15 for revenue from contracts with customers, IFRS 16 for leases).  
    4. **Compliance Analyis**: Check if the  transaction complies with the identified IFRS standards. This includes verifying recognition, measurement, presentation, and disclosure requirements. flags transactions that deviate from expected patterns or fail to meet specific IFRS criteria, indicating potential compliance issues.  
    5. **Correct Suggestions**: Correction Suggestions: For transactions flagged as non-compliant, the system provides detailed explanations of the compliance issues and suggests corrective actions, such as adjusting the transaction amounts, changing the accounts involved, or adding necessary disclosures.  

    """,
        llm=llm_gpt4_0613,
        verbose=True,
        max_function_calls=10,
    )

    return ifrs_agent



