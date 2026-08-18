import re


# =========================================================
# FINANCE CATEGORIES
# =========================================================

CATEGORIES = [
    "food & dining",
    "shopping",
    "travel",
    "bills & utilities",
    "entertainment",
    "healthcare",
    "education"
]


# =========================================================
# INTENT ANALYZER
# =========================================================

def analyze(text: str):

    q = text.lower().strip()

    intent = "general"


    # =====================================================
    # GREETING
    # =====================================================

    greeting_words = [
        "hi",
        "hello",
        "hey",
        "hii",
        "helo",
        "good morning",
        "good afternoon",
        "good evening"
    ]


    if q in greeting_words:

        intent = "greeting"


    # =====================================================
    # CASUAL CONVERSATION
    # =====================================================

    elif any(x in q for x in [
        "how are you",
        "how r you",
        "how are u",
        "what's up",
        "whats up",
        "what are you doing",
        "tell me something",
        "talk to me",
        "lets talk",
        "let's talk",
        "baat cheet",
        "baat karte",
        "kya haal",
        "kya scene"
    ]):

        intent = "casual_chat"


    # =====================================================
    # TRANSACTIONS
    # =====================================================

    elif any(x in q for x in [
        "recent transaction",
        "latest transaction",
        "transactions",
        "transaction history",
        "transaction",
        "activity",
        "show my transactions",
        "show transactions",
        "transaction activity",
        "recent activity"
    ]):

        intent = "transactions"


    # =====================================================
    # CATEGORY ANALYSIS
    # =====================================================

    elif any(x in q for x in [
        "category",
        "categories",
        "breakdown",
        "spending by",
        "where did i spend",
        "where am i spending",
        "which category",
        "top category",
        "highest category",
        "lowest category",
        "category wise",
        "category-wise"
    ]):

        intent = "category_summary"


    # =====================================================
    # FINANCIAL ANALYSIS
    # =====================================================

    elif any(x in q for x in [
        "analyze my spending",
        "analyse my spending",
        "analyze my finances",
        "analyse my finances",
        "spending pattern",
        "spending behaviour",
        "spending behavior",
        "financial health",
        "how is my spending",
        "how is my spending looking",
        "am i spending too much",
        "biggest problem",
        "biggest expenses",
        "biggest spending",
        "financial situation",
        "assess my spending",
        "analyze my transaction",
        "analyse my transaction",
        "analyze my transactions",
        "analyse my transactions"
    ]):

        intent = "financial_analysis"


    # =====================================================
    # FINANCIAL ADVICE
    # =====================================================

    elif any(x in q for x in [
        "financial advice",
        "give me advice",
        "give me some advice",
        "what should i do with my money",
        "how can i save",
        "save more money",
        "saving money",
        "save money",
        "improve my finances",
        "improve my financial",
        "reduce my expenses",
        "reduce expenses",
        "reduce spending",
        "cut my expenses",
        "cut expenses",
        "spending habits",
        "financial plan",
        "money management",
        "manage my money",
        "financial coach",
        "what should i change",
        "how should i manage my money",
        "how can i manage my money"
    ]):

        intent = "financial_advice"


    # =====================================================
    # TOTAL SPENDING
    # =====================================================

    elif any(x in q for x in [
        "total spending",
        "total spend",
        "how much did i spend",
        "how much have i spent",
        "how much money did i spend",
        "overall spending",
        "overall spend",
        "total expenses",
        "total expense",
        "how much have i spent overall",
        "how much did i spend overall",
        "how much money have i spent"
    ]):

        intent = "spending_total"


    # =====================================================
    # BUDGET
    # =====================================================

    elif any(x in q for x in [
        "budget",
        "budget left",
        "remaining budget",
        "how much budget",
        "within my budget",
        "budget used",
        "manage my budget",
        "budget strategy",
        "monthly budget",
        "budget remaining",
        "how much of my budget",
        "how much budget do i have left"
    ]):

        intent = "budget"


    # =====================================================
    # BALANCE
    # =====================================================

    elif any(x in q for x in [
        "balance",
        "account balance",
        "my balance",
        "available balance",
        "how much balance",
        "available amount",
        "how much is available",
        "pending amount",
        "how much is pending"
    ]):

        intent = "balance"


    # =====================================================
    # KNOWLEDGE / RAG
    # =====================================================
    #
    # IMPORTANT:
    # Do NOT use broad phrases like:
    # "what is", "explain", "how does"
    #
    # Otherwise every general question goes to RAG.
    #


    elif any(x in q for x in [

        # Credit
        "credit score",
        "credit history",
        "credit report",

        # Savings
        "emergency fund",

        # Investments
        "compound interest",
        "investing",
        "investment",

        # Budgeting concepts
        "50/30/20",
        "budgeting rule",

        # Transactions
        "pending transaction",
        "completed transaction",
        "recurring transaction",

        # Finance FAQ
        "finance faq",
        "finance faq",
        "financial faq",

        # Explicit FAQ
        "faq"
    ]):

        intent = "knowledge"


    # =====================================================
    # CATEGORY DETECTION
    # =====================================================

    found_category = next(
        (
            c
            for c in CATEGORIES
            if c in q
        ),
        None
    )


    # =====================================================
    # NUMBER DETECTION
    # =====================================================

    numbers = re.findall(
        r"\b\d+(?:\.\d+)?\b",
        q
    )


    # =====================================================
    # RESULT
    # =====================================================

    return {
        "intent": intent,
        "category": found_category,
        "numbers": numbers
    }