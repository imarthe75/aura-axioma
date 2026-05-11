from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain.tools import Tool
from app.services.scd2_manager import SCD2Manager
import os

class CatalogAgent:
    def __init__(self):
        # This will require OPENAI_API_KEY or similar from environment
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        
    def get_tools(self):
        return [
            Tool(
                name="SearchGeo",
                func=lambda q: SCD2Manager(target_table="codigos_postales", natural_key="cp", schema="geo").search(q),
                description="Busca códigos postales, estados o municipios en México."
            ),
            Tool(
                name="SearchFiscal",
                func=lambda q: SCD2Manager(target_table="sat_productos", natural_key="clave", schema="fiscal").search(q),
                description="Busca claves de productos o servicios del SAT."
            )
        ]

    def ask(self, question: str):
        # Simplified agent execution
        # In a real scenario, we would use a more complex prompt
        prompt = hub.pull("hwchase17/react")
        agent = create_react_agent(self.llm, self.get_tools(), prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.get_tools(), verbose=True)
        return agent_executor.invoke({"input": question})
