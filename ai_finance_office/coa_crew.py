import openai
import os
from pathlib import Path  
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

import autogen
import os
import openai

from llama_index.core.tools import BaseTool 
from .agent_as_tools import coa_agent, ifrs_react_agent

# from pydantic import BaseModel, Field
# from typing import Optional, Type, Annotated

os.environ["OPENAI_API_KEY"] ="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"
openai.api_key  = os.getenv('OPENAI_API_KEY')

config_list = [
    {
        "model": "gpt-4-1106-preview",
        "api_key": os.getenv('OPENAI_API_KEY'),
    }
]

llm_config = {
    "seed": 42,  # change the seed for different trials
    "temperature": 0,
    "config_list": config_list,
    "timeout": 600
}



# Helper Function
class CoaStoreTool(BaseTool):
    name = "chart_of_account_tool"
    description = "Use this tool when you need account information and account meta data." 
    args = {
            "message": {
                "type": "string",
                "description": "The question to ask in relation to account store and web search queries.",
            }
        }
    required = "message"

    def __init__(self, coa_agent):
        self.coa_agent = coa_agent

    def _run(self, message: str):
        # Add base instruction to message 
        message = message + " Show me all accounts from the account store in the format `{ 'account_name': 'Inventory of aggregates', 'balance': 'Dr', 'level': 4, 'account_type': 'Assets', 'financial_statement_type': 'Balance Sheet'}`"
    	
        r = self.coa_agent.chat(message)
        return r.response

class IfrsTool(BaseTool):
    name = "ifrs_tool"
    description = "Use this tool when you need accounting standard information from IFRS standards." 
    args = {
            "message": {
                "type": "string",
                "description": "The question to ask in relation IFRS documentation.",
            }
        }
    required = "message"

    def __init__(self, ifrs_agent):
        self.ifrs_agent = ifrs_agent

    def _run(self, message: str):
        r = self.ifrs_agent.chat(message)
        return r.response

def generate_llm_config(tool):
    # Define the function schema based on the tool's args_schema
    function_schema = {
        "name": tool.name.lower().replace(" ", "_"),
        "description": tool.description,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }

    if tool.args is not None:
        function_schema["parameters"]["properties"] = tool.args
    
    if tool.required is not None:
        function_schema["parameters"]["required"].append(tool.required)

    return function_schema

def get_function_spec(function_list):

    llm_config_assistant = {
        # "Seed" : 42,
        "temperature": 0,
            "functions":[generate_llm_config(tool) for tool in function_list],
        "config_list": config_list,
        "timeout": 120,
    }

    return llm_config_assistant


def build_crew():
    pass


# Core Function
class CoaCew():
    
    def __init__(self):
        
        # Init sub level agents
        print("Load Sub Agents and Vectore Store Data...")
        self.CoaAgent = coa_agent(agent_type = "lats")
        self.coa_store_tool = CoaStoreTool(self.CoaAgent)

        self.IfrsAgent = ifrs_react_agent()
        self.ifrs_tool = IfrsTool(self.IfrsAgent)

        # Get Function Spec
        functions_list= [self.coa_store_tool, self.ifrs_tool]  
        self.functions_spec = get_function_spec(functions_list)

        # Set llm config
        self.llm_config = llm_config
        
        # Function map for autogen
        self.function_map={
            self.coa_store_tool.name: self.coa_store_tool._run,
            self.ifrs_tool.name: self.ifrs_tool._run,
        }

    def setup_crew(self):
        #*************
        # BUILD CREW
        #************

        # RetrieveUserProxyAgent
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            code_execution_config={
                "work_dir": "tmp",
                "use_docker": False,
            },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
        )

        # Register the tool and start the conversation
        self.user_proxy.register_function(self.function_map)


        # Account store assistant 
        system_message_account_store_assistant = """
        # Description: 
        This agent has direct access to the account store using the function `chart_of_account_tool` that contains all possible accounts and its meta data. 
        Your primary role is to provide the necessary account data to other agents upon request.

        # Responsibilities: 
        Retrieve and send account data from the function `chart_of_account_tool` to the ChartBuilderAgent based on specific queries or criteria. 


        """

        self.account_store_agent = autogen.AssistantAgent(
                    name="account_store_agent",
                    llm_config=self.functions_spec,
                    system_message = system_message_account_store_assistant
                    
                )

        # chart builder
        system_message_chart_builder = """
        # Description: 
        You are responsible for constructing a chart of accounts. You receive receives account data and account meta data from the AccountStoreAgent and uses it to build or modify the chart of accounts according to the user's specifications or business rules. 

        # Responsibilities: 
        Build or update the chart of accounts using the data provided, apply business rules or customization options, and send the draft chart to the ValidationAgent for review. 

        """

        self.chart_builder_agent = autogen.AssistantAgent(
                    name="chart_builder_agent",
                    llm_config=self.llm_config,
                    system_message = system_message_chart_builder
                    
                )

        # Validate agent
        system_message_validation_agent = """
        # Description:  
        This agent has direct access to the accounting standard form IFRS using the function `ifrs_tool`. 
        Use the function `ifrs_tool` with a plane text as input. Call the function with a 'IFRS' accounting standard request.

        Checks the integrity and correctness of the chart of accounts created by the ChartBuilderAgent. 
        This includes validating the structure against regulatory and company-specific standards.


        # Responsibilities: 
        Validate the proposed chart of accounts unsing the tool `ifrs_tool`, ensure compliance with standards, and provide feedback or approval back to the ChartBuilderAgent.  
        """

        self.validation_agent= autogen.AssistantAgent(
                    name="validation_agent",
                    llm_config=self.functions_spec,
                    system_message = system_message_validation_agent
                    
                )

        # Group Chat 
        groupchat = autogen.GroupChat(agents=[self.user_proxy, self.chart_builder_agent, self.account_store_agent, self.validation_agent], 
                                    messages=[], 
                                    max_round=20, 
                                    admin_name="chart_builder_agent", 
                                    speaker_selection_method="round_robin"
                                    )

        system_message = """
            # Workflow

            1. UserProxyAgent to ChartBuilderAgent
            Task: UserProxyAgent collects initial requirements from the user for the custom chart of accounts and communicates these to the ChartBuilderAgent.

            2. ChartBuilderAgent to AccountStoreAgent
            Task: Once the requirements are understood, the ChartBuilderAgent requests specific account data from the AccountStoreAgent needed to build the chart.

            3. AccountStoreAgent to ChartBuilderAgent
            Task: AccountStoreAgent retrieves the necessary account data from the store and sends it back to the ChartBuilderAgent.

            4.ChartBuilderAgent to ValidationAgent
            Task: After constructing the initial chart of accounts, the ChartBuilderAgent submits it to the ValidationAgent for compliance checking and validation.

            5. ValidationAgent to ChartBuilderAgent
            Task: ValidationAgent returns feedback or approval to the ChartBuilderAgent. If modifications are required, the ChartBuilderAgent adjusts the chart accordingly.

            6. ChartBuilderAgent to AccountStoreAgent
            Task: After the ChartBuilderAgent received the valudation from the ValidationAgent, the ChartBuilderAgent request an update from the AccountStore Agent accordingly to the required modification.

            Repeat  2.-6.  until the chart is finalized!
            
            7. ChartBuilderAgent to UserProxyAgent
            Task: Once the chart is finalized and validated, the ChartBuilderAgent sends the completed chart back to the UserProxyAgent.

            7. UserProxyAgent to User
            Task: UserProxyAgent presents the final chart of accounts to the user and handles any further interactions or modifications requested by the user.

        """

        self.manager = autogen.GroupChatManager(
            groupchat=groupchat, 
            llm_config=self.llm_config,
            system_message = system_message,

            )
        
    def _reset_agents(self):
        self.user_proxy.reset()
        self.account_store_agent.reset()
        self.chart_builder_agent.reset()
        self.validation_agent.reset()
        # self.groupchat.reset()

    def chat(self, task):
        self._reset_agents()

         # Start chatting with userProxi as this is the user proxy agent.  

        self.user_proxy.initiate_chat(
            self.manager, 
            message= task #self.user_proxy.message_generator,
            # problem = task
        )

        






