import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .db import (
    init_db,
    recent_transactions,
    spending_total,
    category_summary,
    search_transactions,
)

from .nlp import analyze
from .rag import RAGRetriever
from .llm import generate_answer


# =========================================================
# PROJECT PATH
# =========================================================

BASE = Path(__file__).resolve().parents[1]


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="FinAssist AI",
    version="2.0.0"
)


# =========================================================
# CORS
# =========================================================

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# REQUEST MODEL
# =========================================================

class ChatRequest(BaseModel):
    message: str


# =========================================================
# DATABASE + RAG INITIALIZATION
# =========================================================

init_db()

rag = RAGRetriever(BASE / "docs")


# =========================================================
# HELPER
# =========================================================

def html_money(n):
    return f"₹{n:,.2f}"


# =========================================================
# FINASSIST DOMAIN GUARD
# =========================================================

# These are legitimate topics that FinAssist is designed
# to answer.

FINANCE_TERMS = [

    # -----------------------------------------------------
    # GENERAL FINANCE
    # -----------------------------------------------------

    "finance",
    "financial",
    "money",
    "income",
    "expense",
    "expenses",
    "spending",
    "spend",
    "spent",
    "saving",
    "savings",

    # -----------------------------------------------------
    # BANKING
    # -----------------------------------------------------

    "bank",
    "banking",
    "bank account",
    "account",
    "balance",
    "transaction",
    "transactions",
    "payment",
    "payments",
    "credit",
    "debit",
    "loan",
    "loans",
    "deposit",
    "withdrawal",
    "interest",
    "cash flow",
    "cashflow",

    # -----------------------------------------------------
    # BUDGET
    # -----------------------------------------------------

    "budget",
    "budgeting",
    "budget plan",
    "monthly budget",
    "budget management",

    # -----------------------------------------------------
    # INVESTMENT
    # -----------------------------------------------------

    "investment",
    "invest",
    "investing",
    "investor",
    "stock",
    "stocks",
    "share",
    "shares",
    "mutual fund",
    "mutual funds",
    "etf",
    "etfs",
    "portfolio",
    "diversification",
    "dividend",
    "capital",
    "asset",
    "assets",
    "risk",
    "return",
    "returns",
    "compound interest",

    # -----------------------------------------------------
    # SALES / BUSINESS FINANCE
    # -----------------------------------------------------

    "sales",
    "sale",
    "selling",
    "revenue",
    "profit",
    "profits",
    "loss",
    "losses",
    "margin",
    "profit margin",
    "business finance",
    "financial analysis",
    "financial planning",
    "financial performance",
    "financial kpi",
    "kpi",

    # -----------------------------------------------------
    # FINANCIAL DATA / DATASET
    # -----------------------------------------------------

    "financial data",
    "financial dataset",
    "finance dataset",
    "transaction data",
    "spending data",
    "sales data",
    "revenue data",
    "dataset",
    "data analysis",
    "financial analysis",

    # -----------------------------------------------------
    # FINASSIST
    # -----------------------------------------------------

    "finassist",
    "finance chatbot",
    "finance ai",
    "financial assistant",
    "banking chatbot",
    "banking ai",
]


# =========================================================
# FINASSIST-SPECIFIC QUESTIONS
# =========================================================

# These are allowed because they directly concern the
# FinAssist application itself.

FINASSIST_TERMS = [

    "finassist",
    "your introduction",
    "your intro",
    "brief of yourself",
    "brief about yourself",
    "tell me about yourself",
    "who are you",
    "what can you do",
    "what do you do",
    "how do you work",
    "how does this model work",
    "how does the model work",
    "how this model works",
    "how does finassist work",
    "how finassist works",
    "how this chatbot works",
    "how this chatbot is working",
    "your architecture",
    "model architecture",
    "finassist architecture",
    "how can you help banks",
    "how can you help banking",
    "how can finassist help banks",
    "how can finassist help banking",
    "banking system use case",
]


# =========================================================
# ILLEGAL / UNSAFE FINANCIAL REQUESTS
# =========================================================

ILLEGAL_TERMS = [

    "hack bank",
    "hack a bank",
    "hack bank account",
    "hack a bank account",
    "steal money",
    "steal someone's money",
    "steal bank account",
    "steal bank credentials",

    "financial fraud",
    "bank fraud",
    "commit fraud",
    "how to commit fraud",
    "how to do fraud",

    "money laundering",
    "launder money",
    "hide illegal income",
    "hide illicit income",
    "illegal income",

    "tax evasion",
    "evade taxes",
    "avoid taxes illegally",

    "fake bank statement",
    "fake financial record",
    "fake transaction",
    "fake transactions",

    "bypass kyc",
    "bypass aml",
    "bypass bank security",
    "bypass banking security",

    "phishing bank",
    "phish a bank",
    "steal credentials",

    "unauthorized access",
    "unauthorized bank access",

    "market manipulation",
    "manipulate stock price",
    "manipulate the market",

    "money mule",
]


# =========================================================
# DOMAIN CHECK
# =========================================================

def is_finance_related(text: str):

    q = text.lower().strip()

    # Direct finance/domain match
    if any(term in q for term in FINANCE_TERMS):
        return True

    # FinAssist-specific questions
    if any(term in q for term in FINASSIST_TERMS):
        return True

    return False


# =========================================================
# ILLEGAL ACTIVITY CHECK
# =========================================================

def is_illegal_request(text: str):

    q = text.lower().strip()

    return any(
        term in q
        for term in ILLEGAL_TERMS
    )


# =========================================================
# OUT-OF-DOMAIN RESPONSE
# =========================================================

def out_of_domain_response():

    return {
        "answer": (
            "I can only help with finance, banking, "
            "sales, investments, and financial-data "
            "related questions."
        ),

        "intent": "out_of_domain",

        "rag_used": False,

        "llm_used": False,

        "data": None
    }


# =========================================================
# ILLEGAL REQUEST RESPONSE
# =========================================================

def illegal_response():

    return {
        "answer": (
            "I can't help with illegal financial activity. "
            "I can help with legitimate finance, banking, "
            "investment, budgeting, or compliance-related "
            "questions."
        ),

        "intent": "restricted",

        "rag_used": False,

        "llm_used": False,

        "data": None
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/api/health")
def health():

    return {
        "status": "ok",
        "records": len(
            recent_transactions(100000)
        )
    }


# =========================================================
# TRANSACTIONS API
# =========================================================

@app.get("/api/transactions")
def transactions(limit: int = 10):

    return {
        "rows": recent_transactions(
            min(limit, 50)
        )
    }


# =========================================================
# SUMMARY API
# =========================================================

@app.get("/api/summary")
def summary():

    return {
        "total_spending": spending_total(),
        "categories": category_summary()
    }


# =========================================================
# MAIN CHAT API
# =========================================================

@app.post("/api/chat")
def chat(req: ChatRequest):

    # =====================================================
    # 0. BASIC INPUT CHECK
    # =====================================================

    user_message = req.message.strip()

    if not user_message:

        return {
            "answer": (
                "Please ask a finance, banking, "
                "sales, investment, or financial-data question."
            ),

            "intent": "empty",

            "rag_used": False,

            "llm_used": False,

            "data": None
        }


    # =====================================================
    # 1. NLP / INTENT DETECTION
    # =====================================================

    n = analyze(user_message)

    intent = n["intent"]


    # =====================================================
    # 2. FAST GREETING
    # =====================================================

    # Greetings are allowed as basic chatbot interaction.

    if intent == "greeting":

        return {
            "answer": (
                "Hey! How can I help you "
                "with your finances today?"
            ),

            "intent": intent,

            "rag_used": False,

            "llm_used": False,

            "data": None
        }


    # =====================================================
    # 3. ILLEGAL ACTIVITY CHECK
    # =====================================================

    # This check happens BEFORE the LLM.

    if is_illegal_request(user_message):

        return illegal_response()


    # =====================================================
    # 4. CASUAL CHAT
    # =====================================================

    # Keep only basic conversational support.
    # We don't send random casual questions to the LLM.

    if intent == "casual_chat":

        return {
            "answer": (
                "I'm here to help with your finances. "
                "Ask me about spending, transactions, "
                "budget, banking, sales, or investments."
            ),

            "intent": intent,

            "rag_used": False,

            "llm_used": False,

            "data": None
        }


    # =====================================================
    # 5. STRICT DOMAIN GUARD
    # =====================================================

    # Anything outside FinAssist's domain is rejected
    # BEFORE SQL, RAG, or LLM processing.

    if not is_finance_related(user_message):

        return out_of_domain_response()


    # =====================================================
    # 6. FAST TOTAL SPENDING
    # =====================================================

    if intent == "spending_total":

        total = spending_total()

        return {
            "answer": (
                f"Your total successful spending is "
                f"<b>{html_money(total)}</b>."
            ),

            "intent": intent,

            "rag_used": False,

            "llm_used": False,

            "data": {
                "type": "spending_total",
                "total": total
            }
        }


    # =====================================================
    # 7. FAST TRANSACTIONS
    # =====================================================

    if intent == "transactions":

        rows = recent_transactions(8)

        return {
            "answer": (
                "Here are your latest transactions "
                "from the demo dataset."
            ),

            "intent": intent,

            "rag_used": False,

            "llm_used": False,

            "data": {
                "type": "transactions",
                "rows": rows
            }
        }


    # =====================================================
    # 8. FAST CATEGORY SUMMARY
    # =====================================================

    if intent == "category_summary":

        cats = category_summary()

        answer = "<br>".join(
            f"<b>{x['category']}</b>: "
            f"{html_money(x['total'])}"
            for x in cats[:7]
        )

        return {
            "answer": answer,

            "intent": intent,

            "rag_used": False,

            "llm_used": False,

            "data": {
                "type": "category_summary",
                "categories": cats
            }
        }


    # =====================================================
    # 9. FINANCIAL ANALYSIS
    # =====================================================

    db_context = ""

    data = None

    fallback = (
        "I couldn't generate a detailed answer right now."
    )


    if intent == "financial_analysis":

        total = spending_total()

        cats = category_summary()

        db_context = f"""
FINANCIAL ANALYSIS DATA

Total successful spending:
{total}

Category-wise spending:
{cats}

Analyze the user's financial activity using ONLY
this supplied data.
"""

        data = {
            "type": "financial_analysis",

            "total_spending": total,

            "categories": cats
        }

        fallback = (
            "I checked your spending data, "
            "but I couldn't generate the analysis."
        )


    # =====================================================
    # 10. FINANCIAL ADVICE
    # =====================================================

    elif intent == "financial_advice":

        total = spending_total()

        cats = category_summary()

        db_context = f"""
USER FINANCIAL DATA

Total successful spending:
{total}

Category-wise spending:
{cats}

Give practical financial suggestions based ONLY
on the supplied financial data.

Do not invent any numbers.
"""

        data = {
            "type": "financial_advice",

            "total_spending": total,

            "categories": cats
        }

        fallback = (
            "I can give you practical suggestions "
            "based on your spending pattern."
        )


    # =====================================================
    # 11. BALANCE
    # =====================================================

    elif intent == "balance":

        db_context = """
SYNTHETIC DEMO ACCOUNT INFORMATION

Balance:
₹86,420

Available:
₹78,950

Pending:
₹7,470

This is synthetic demo data.
"""

        fallback = (
            "The demo account balance is "
            "<b>₹86,420</b>. "
            "This is synthetic demo data."
        )


    # =====================================================
    # 12. BUDGET
    # =====================================================

    elif intent == "budget":

        total = spending_total()

        db_context = f"""
SYNTHETIC DEMO BUDGET

Budget:
₹500,000

Total successful spending:
{total}

Use these figures when answering the user's
budget-related question.
"""

        data = {
            "type": "budget",

            "budget": 500000,

            "total_spending": total
        }

        fallback = (
            f"Your demo budget is "
            f"<b>₹5,00,000</b>, and your successful "
            f"spending is <b>{html_money(total)}</b>."
        )


    # =====================================================
    # 13. KNOWLEDGE / FAQ
    # =====================================================

    elif intent == "knowledge":

        db_context = """
This is a general finance knowledge question.

No account-specific database information is required.

Use the supplied RAG context when relevant.

If the RAG context does not contain the answer,
answer the finance-related educational question
using legitimate general financial knowledge.

Do not invent personal financial data.
"""

        fallback = (
            "I couldn't generate an answer "
            "to that finance question."
        )


    # =====================================================
    # 14. GENERAL FINANCE / FINASSIST QUESTIONS
    # =====================================================

    else:

        db_context = """
No specific account database query was identified.

This is an allowed FinAssist-domain question.

The question may concern:

- Finance
- Banking
- Sales
- Investments
- Financial data
- Financial datasets
- FinAssist
- FinAssist architecture
- Legitimate banking use cases

Answer ONLY within these domains.

If the user asks about FinAssist:
explain FinAssist using the system instructions.

If the user asks how FinAssist works:
explain:

NLP
→ SQL
→ RAG
→ Llama
→ FastAPI
→ Frontend

If the user asks how FinAssist helps banks:
explain legitimate banking use cases.

Do not answer unrelated topics.

Do not invent personal financial information.
"""

        fallback = (
            "I couldn't generate a detailed answer right now."
        )


    # =====================================================
    # 15. RAG RETRIEVAL
    # =====================================================

    # IMPORTANT:
    # RAG is ONLY used for finance knowledge questions.
    #
    # General FinAssist questions don't need RAG.
    # This also reduces latency.

    if intent == "knowledge":

        rag_docs = rag.retrieve(
            user_message,
            3
        )

    else:

        rag_docs = []


    rag_context = "\n\n---\n\n".join(
        rag_docs
    )


    # =====================================================
    # 16. HUGGING FACE / LLAMA
    # =====================================================

    ai = generate_answer(
        user_message,
        db_context,
        rag_context
    )


    # =====================================================
    # 17. FINAL ANSWER
    # =====================================================

    if ai:

        answer = ai.replace(
            "\n",
            "<br>"
        )

    else:

        answer = fallback


    # =====================================================
    # 18. RESPONSE
    # =====================================================

    return {

        "answer": answer,

        "intent": intent,

        "rag_used": bool(rag_docs),

        "llm_used": bool(ai),

        "data": data
    }