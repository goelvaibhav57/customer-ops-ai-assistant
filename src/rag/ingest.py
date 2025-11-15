from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from pathlib import Path

DATA_RAW = Path("data/raw")

VEC_DIR = Path("../data/vectorstore")

def build_index():
    api_guide_loader = TextLoader('../data/raw/api_guide.md')
    api_guide_doc = api_guide_loader.load()

    billing_module_loader = TextLoader('../data/raw/billing_module.md')
    billing_module_doc = billing_module_loader.load()

    campaigns_module_loader = TextLoader('../data/raw/campaigns_module.md')
    campaigns_module_doc = campaigns_module_loader.load()

    overview_loader = TextLoader('../data/raw/overview.md')
    overview_doc = overview_loader.load()

    pricing_plans_loader = TextLoader('../data/raw/pricing_plans.md')
    pricing_plans_doc = pricing_plans_loader.load()

    security_faq_loader = TextLoader('../data/raw/security_faq.md')
    security_faq_doc = security_faq_loader.load()

    support_module_loader = TextLoader('../data/raw/support_module.md')
    support_module_doc = support_module_loader.load()

    api_guide_doc[0].metadata["source"] = "api_guide.md"
    billing_module_doc[0].metadata["source"]="billing_module.md"
    campaigns_module_doc[0].metadata["source"]="campaigns_module.md"
    overview_doc[0].metadata["source"] = "overdue.md"
    pricing_plans_doc[0].metadata["source"] = "pricing_plan.md"
    security_faq_doc[0].metadata["source"] = "security_faq.md"
    support_module_doc[0].metadata["source"] = "support_module.md"

    docs = api_guide_doc + billing_module_doc + campaigns_module_doc + overview_doc + pricing_plans_doc + security_faq_doc + support_module_doc



    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Build FAISS from chunks (with OpenAI or HF embeddings)
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(str(VEC_DIR))
    return docs