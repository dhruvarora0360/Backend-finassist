from pathlib import Path


class RAGRetriever:
    """
    Lightweight FinAssist RAG Retriever.

    Uses keyword-based retrieval only.

    This version is designed for low-memory deployment
    environments such as Render's limited-memory instances.

    Finance knowledge is loaded from Markdown files
    inside the docs directory.
    """

    def __init__(self, docs_dir):

        self.docs_dir = Path(docs_dir)

        self.documents = []

        self._load_documents()


    # =====================================================
    # LOAD DOCUMENTS
    # =====================================================

    def _load_documents(self):

        if not self.docs_dir.exists():

            print(
                f"RAG docs directory not found: "
                f"{self.docs_dir}"
            )

            return


        for path in self.docs_dir.glob("*.md"):

            try:

                text = path.read_text(
                    encoding="utf-8"
                ).strip()


                if text:

                    self.documents.append(text)


            except Exception as exc:

                print(
                    f"RAG document error "
                    f"{path.name}: {exc}"
                )


        print(
            f"RAG documents loaded: "
            f"{len(self.documents)}"
        )


    # =====================================================
    # KEYWORD SEARCH
    # =====================================================

    def _keyword_search(
        self,
        query,
        k
    ):

        query_terms = set(
            query.lower().split()
        )


        scored = []


        for document in self.documents:

            document_lower = document.lower()


            score = sum(
                1
                for term in query_terms
                if term in document_lower
            )


            scored.append(
                (
                    score,
                    document
                )
            )


        scored.sort(
            key=lambda item: item[0],
            reverse=True
        )


        return [
            document
            for score, document in scored[:k]
            if score > 0
        ]


    # =====================================================
    # RETRIEVE
    # =====================================================

    def retrieve(
        self,
        query,
        k=3
    ):

        if not self.documents:

            return []


        k = max(
            1,
            min(
                k,
                len(self.documents)
            )
        )


        return self._keyword_search(
            query,
            k
        )