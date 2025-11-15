from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from pathlib import Path

VEC_DIR = Path("../data/vectorstore")

def get_retriever():
    try:
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.load_local(
            str(VEC_DIR),
            embeddings,
            allow_dangerous_deserialization=True
        )
        return vectorstore.as_retriever()

    except FileNotFoundError as e:
        print(f"[ERROR] Vector store directory not found: {VEC_DIR}")
        raise e

    except Exception as e:
        print(f"[ERROR] Failed to load retriever: {e}")
        raise e