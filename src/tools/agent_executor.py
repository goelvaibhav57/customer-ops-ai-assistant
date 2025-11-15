from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.openai_functions_agent.base import create_openai_functions_agent
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from .csv_tools import get_tools
from rag.prompts import TOOL_PROMPT

def get_executor():
    prompt = ChatPromptTemplate.from_messages([
        ("system", TOOL_PROMPT),
        MessagesPlaceholder("messages"),
        MessagesPlaceholder("agent_scratchpad")
    ])
    tools = get_tools()
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )