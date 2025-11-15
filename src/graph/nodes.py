from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from .state import AgentState
from rag.retriever import get_retriever
from rag.prompts import CRM_RETRIEVAL_PROMPT, ROUTER_PROMPT, RATIONALE_PROMPT, SYNTHESIZE_PROMPT, ESCALATION_PROMPT
from tools.agent_executor import get_executor
from langchain_core.output_parsers import StrOutputParser
from langgraph.types import Command
import json

llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

def faq_node(state: AgentState):
    try:
        CRM_RETRIEVAL_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(CRM_RETRIEVAL_PROMPT)
        faq_chain = (
            CRM_RETRIEVAL_PROMPT_TEMPLATE | llm
        )
        faq_retriever = get_retriever()
        retrieved_docs = faq_retriever.invoke(state.query)
        response = faq_chain.invoke({"question": state.query, "context": retrieved_docs})
        data = json.loads(response.content)
        state.answer = data.get("answer")
        state.evidence = data.get("evidence")
        if state.evidence is None or len(state.evidence) == 0:
            return Command(goto="Escalate", update=state)
        else:
            return Command(goto="Synthesize", update=state)
    except Exception as e:
        state.errors.append("Error in getting repsonse from RAG")
        return Command(goto="Escalate", update=state)


def data_lookup_node(state: AgentState):
    try:
        executor = get_executor()
        result = executor.invoke({"messages": state.history})
        final_answer = result.get("output", "")
        data = json.loads(final_answer)
        print("--data--")
        print(data)
        content = data.get("answer")
        if isinstance(content, dict):
            answer = json.dumps(content)
            state.answer = answer.replace("'", "")
        elif isinstance(content, str):
            state.answer = content
        state.evidence = data.get("sources")
        steps = result.get("intermediate_steps", [])
        if state.evidence is None or len(state.evidence) == 0:
            return Command(goto="Escalate", update=state)
        else:
            return Command(goto="Synthesize", update=state)
    except Exception as e:
        state.errors.append("Error in getting repsonse from TOOLS")
        return Command(goto="Escalate", update=state)


def escalate_node(state: AgentState):
    print("--escalation--")
    ESCALATION_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(ESCALATION_PROMPT)

    escalate_chain = (
        ESCALATION_PROMPT_TEMPLATE | llm | StrOutputParser()
    )
    print("--chain preparation--")
    error_text = "\n".join(state.errors)
    context = "\n".join(state.history)
    response = escalate_chain.invoke({"answer": state.answer, "context": context, "error_text": error_text})
    print(response)
    state.answer = response
    return state

def synthesize_node(state: AgentState):
    print("--In Synthesize--")
    history = state.history
    history.append(f"AIMessage(content='{state.answer})")
    state.history = history
    SYNTHESIZE_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(SYNTHESIZE_PROMPT)

    synthesize_chain = (
        SYNTHESIZE_PROMPT_TEMPLATE | llm | StrOutputParser()
    )
    evidence_text = "\n".join(state.evidence)
    response = synthesize_chain.invoke({"answer": state.answer, "evidence": evidence_text})
    state.answer = response
    return state

def routing_request(state: AgentState):
    if state.intent == "DataLookup":
        return "rationale_node"
    else:
        return state.intent

def router_node(state: AgentState):

    router_prompt = ChatPromptTemplate.from_template(ROUTER_PROMPT)

    router_chain = router_prompt | llm | StrOutputParser()

    # join list of strings into readable format
    history_text = "\n".join(state.history)
    query = state.query

    result = router_chain.invoke({'history_text':history_text, 'query':query})
    history = state.history
    history.append(f'HumanMessage(content=" {state.query}")')
    state.intent = result
    return state



def rationale_node(state:AgentState):
    rationale_prompt = ChatPromptTemplate.from_template(RATIONALE_PROMPT)
    rationale_chain = rationale_prompt | llm | StrOutputParser()
    history_text = "\n".join(state.history)
    query = state.query
    result = rationale_chain.invoke({'history':history_text, 'query':query})
    return state