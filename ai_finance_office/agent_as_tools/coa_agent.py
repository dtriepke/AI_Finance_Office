import openai
import os
# from pathlib import Path  
import urllib.parse
from typing import Optional
import requests

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
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.postprocessor import LLMRerank
from llama_index.core.schema import Document
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.tools.tool_spec.base import BaseToolSpec
from llama_index.core.tools.tool_spec.load_and_search.base import LoadAndSearchToolSpec
from llama_index.core import  ServiceContext

from llama_index.core.agent import ReActAgent
from llama_index.agent.lats import LATSAgentWorker
from llama_index.core.agent import AgentRunner

from .utils import create_index_from_db_with_DeepLakeVectorStore


#*******
# COA
#******

# VECTORE STORE
def get_account_store_query_tool():
    # create index fom vectore store
    index = create_index_from_db_with_DeepLakeVectorStore("dennistriepke", "coa_account_store", overwrite = False)

    # configure retriever
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=20,
    )

    # configure response synthesizer
    response_synthesizer = get_response_synthesizer(response_mode="tree_summarize", structured_answer_filtering=True)


    # configure post processing
    service_context = ServiceContext.from_defaults(llm=llm_gpt3_turbo_0125)
    postprocessor = [LLMRerank(top_n=2, service_context=service_context), SimilarityPostprocessor(similarity_cutoff=0.7)]

    # assemble query engine
    account_store_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer,
        node_postprocessors=postprocessor
    )

    # Define the Query engine tool for each document
    query_tool_account_store = QueryEngineTool.from_defaults(
        query_engine=account_store_engine,
        name="account_store",
        description=("""
                    Provides information for chart of accounts.

                    Use this tool to get following info for a single account:  
                    - Account Name  
                    - Balance: (Specify Debit or Credit Account)  
                    - Account Type  
                    - Financial Statement Type  
                    - Account Description (what it used for and IFRS and GAAP information)  
                    
                    Use a detailed plain text question as input to the tool.  
                    Make sure you response is designed in length and format for an LLM Agent (not human). The agent will recive your result and syntehize the final answer.  
                    
                    """
        ),
    )

    return query_tool_account_store

#WEB SEARCH TOOL
def get_web_search_query_tool():
    QUERY_URL_TMPL = (
        "https://www.googleapis.com/customsearch/v1?key={key}&cx={engine}&q={query}"
    )


    class GoogleSearchToolSpec(BaseToolSpec):
        """Google Search tool spec."""

        spec_functions = ["google_search"]

        def __init__(self, key: str, engine: str, num: Optional[int] = None) -> None:
            """Initialize with parameters."""
            self.key = key
            self.engine = engine
            self.num = num

        def google_search(self, query: str):
            """
            Make a query to the Google search engine to receive a list of results.

            Args:
                query (str): The query to be passed to Google search.
                num (int, optional): The number of search results to return. Defaults to None.

            Raises:
                ValueError: If the 'num' is not an integer between 1 and 10.
            """
            url = QUERY_URL_TMPL.format(
                key=self.key, engine=self.engine, query=urllib.parse.quote_plus(query)
            )

            if self.num is not None:
                if not 1 <= self.num <= 10:
                    raise ValueError("num should be an integer between 1 and 10, inclusive")
                url += f"&num={self.num}"

            response = requests.get(url)
            return [Document(text=response.text)]
        
    gsearch_tools  = GoogleSearchToolSpec(key='AIzaSyCQFnxl22R0aFF-dEh4vHH7o0IEQ3gY1Y8', engine= '431e5ac5e35c049c3', num=10).to_tool_list()

    # for tool in [*gsearch_tools]:
    #     print(tool.metadata.name)
    #     print(tool.metadata.description)

    # print("Wrapping " + gsearch_tools[0].metadata.name)
    gsearch_load_and_search_tools = LoadAndSearchToolSpec.from_defaults(
                gsearch_tools[0],
                name="google_search_tool", 
                description=f"""\
            Useful for any queries that requires web search. 
            """
            ).to_tool_list()

    web_search_agent = ReActAgent.from_tools(
        gsearch_load_and_search_tools, 
        llm=llm_gpt4_0613,
        system_prompt="""
        You are a specialized web search agent designed to answer queries with  a web search request.  
        You must ALWAYS use at least one of the tools provided when answering a question; do NOT rely on prior knowledge. 
        Make sure you response is designed in length and format for an LLM Agent (not human). The agent will recive your result and syntehize the final answer. 
        """,
        verbose=True
    )

    # Web search Agent
    web_search_summary = ("""
        This tool contains an agent that has access internet.
        Use this tool if you want to research knowledge.

    """
    )
    web_search_tool = QueryEngineTool(
        query_engine=web_search_agent,
        metadata=ToolMetadata(
            name="tool_web_search",
            description=web_search_summary,
        ),
    )

    return web_search_tool

# COA AGENT
def coa_agent(agent_type = "lats", sytstem_message = None):

    # Collect tools in a list
    all_tools = []
    query_tool_account_store = get_account_store_query_tool()
    web_search_tool = get_web_search_query_tool()
    all_tools.append(query_tool_account_store)
    all_tools.append(web_search_tool)

    
    if not sytstem_message:
        system_message = system_message = """
        You are a specialized accountant with access to the tools account store `account_store` and a web search via `tool_web_search`. 
        Once you received the query, plan the which tool to use. 

        ALWAYS begin to plan to answer the query with using the `account_store` tool.  
            
            Thought: I can use the account_store tool to retrieve this information.  
            Action: account_store  
            Action Input {'input': ...}
            ...
        
        If no relevant account is found, respond with "I do not have a matching account" and use the `tool_web_search` for suggesting an account.
        
        Response wiht with the account information:
                - account_name
                - balance
                - level
                - account_type
                - financial_statement_type        
        In the format: `{ 'account_name': 'Inventory of aggregates', 'balance': 'Dr', 'level': 4, 'account_type': 'Assets', 'financial_statement_type': 'Balance Sheet'}`
    """

    if agent_type == "recat":
        agent = ReActAgent.from_tools(
            tools = all_tools ,
            max_function_calls=20,
            llm= llm_gpt4_0613, #OpenAI(temperature=0.1, model="gpt-4-0613"),
            verbose=True,
            system_prompt= system_message
        )
    
    if agent_type == "lats":
        coa_lats_agent_worker = LATSAgentWorker.from_tools(
            tools = all_tools ,
            num_expansions=2,
            max_rollouts=3, 
            max_function_calls=20,
            llm= llm_gpt4_0613, #OpenAI(temperature=0.1, model="gpt-4-0613"),
            verbose=True,
            system_prompt= system_message
        )

        agent = AgentRunner(coa_lats_agent_worker)

    return agent










