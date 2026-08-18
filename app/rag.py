from pathlib import Path
import numpy as np


class RAGRetriever:
    """
    FinAssist RAG Retriever.

    Uses:
    1. Sentence Transformers + FAISS when available.
    2. Keyword matching as a fallback.

    RAG is intended for finance knowledge stored
    inside the docs directory.
    """

    def __init__(self, docs_dir):

        self.docs_dir = Path(docs_dir)

        self.documents = []

        self.model = None

        self.index = None

        self._load_documents()

        self._build_semantic_index()


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
    # BUILD FAISS INDEX
    # =====================================================

    def _build_semantic_index(self):

        if not self.documents:

            return


        try:

            from sentence_transformers import (
                SentenceTransformer
            )

            import faiss


            print(
                "Loading RAG embedding model..."
            )


            self.model = SentenceTransformer(
                "all-MiniLM-L6-v2"
            )


            vectors = self.model.encode(
                self.documents,
                normalize_embeddings=True
            )


            vectors = np.asarray(
                vectors,
                dtype="float32"
            )


            self.index = faiss.IndexFlatIP(
                vectors.shape[1]
            )


            self.index.add(vectors)


            print(
                "RAG semantic search enabled."
            )


        except Exception as exc:

            self.model = None

            self.index = None


            print(
                "RAG semantic search unavailable."
            )

            print(
                f"Using keyword fallback: {exc}"
            )


    # =====================================================
    # SEMANTIC SEARCH
    # =====================================================

    def _semantic_search(
        self,
        query,
        k
    ):

        if not self.model or not self.index:

            return []


        try:

            query_vector = self.model.encode(
                [query],
                normalize_embeddings=True
            )


            query_vector = np.asarray(
                query_vector,
                dtype="float32"
            )


            number = min(
                k,
                len(self.documents)
            )


            scores, ids = self.index.search(
                query_vector,
                number
            )


            results = []


            for document_id in ids[0]:

                if document_id >= 0:

                    results.append(
                        self.documents[document_id]
                    )


            return results


        except Exception as exc:

            print(
                f"RAG semantic search error: {exc}"
            )

            return []


    # =====================================================
    # KEYWORD FALLBACK
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


        # -------------------------------------------------
        # Try semantic search first
        # -------------------------------------------------

        if self.model and self.index:

            results = self._semantic_search(
                query,
                k
            )


            if results:

                return results


        # -------------------------------------------------
        # Keyword fallback
        # -------------------------------------------------

        return self._keyword_search(
            query,
            k
        )