# backend/tests/test_rag.py

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document


# ══════════════════════════════════════════════════════════════════════════════
# test ingest
# ══════════════════════════════════════════════════════════════════════════════

class TestIngest:

    def test_validate_unsupported_extension_raises(self):
        from app.utils.helpers import validate_file_extension
        with pytest.raises(ValueError):
            validate_file_extension("image.png")

    def test_validate_supported_extensions(self):
        from app.utils.helpers import validate_file_extension
        assert validate_file_extension("report.pdf")  == ".pdf"
        assert validate_file_extension("notes.txt")   == ".txt"
        assert validate_file_extension("file.docx")   == ".docx"

    @patch("app.rag.ingest.FAISS")
    @patch("app.rag.ingest.splitter")
    @patch("app.rag.ingest.load_documents")
    def test_ingest_document_creates_new_index(
        self, mock_load, mock_splitter, mock_faiss
    ):
        from app.rag.ingest import ingest_document

        # Mock: load returns 1 doc, splitter returns 3 chunks
        mock_load.return_value    = [MagicMock()]
        mock_splitter.split_documents.return_value = [
            MagicMock(), MagicMock(), MagicMock()
        ]
        mock_faiss.from_documents.return_value = MagicMock()

        with patch("app.rag.ingest.os.path.exists", return_value=False):
            result = ingest_document("fake/path/doc.pdf")

        assert result == 3
        mock_faiss.from_documents.assert_called_once()

    @patch("app.rag.ingest.FAISS")
    @patch("app.rag.ingest.splitter")
    @patch("app.rag.ingest.load_documents")
    def test_ingest_document_updates_existing_index(
        self, mock_load, mock_splitter, mock_faiss
    ):
        from app.rag.ingest import ingest_document

        mock_load.return_value = [MagicMock()]
        mock_splitter.split_documents.return_value = [MagicMock(), MagicMock()]

        mock_vs = MagicMock()
        mock_faiss.load_local.return_value = mock_vs

        with patch("app.rag.ingest.os.path.exists", return_value=True):
            result = ingest_document("fake/path/doc.pdf")

        assert result == 2
        mock_vs.add_documents.assert_called_once()
        mock_vs.save_local.assert_called_once()


# ══════════════════════════════════════════════════════════════════════════════
# test retriever
# ══════════════════════════════════════════════════════════════════════════════

class TestRetriever:

    @patch("app.rag.retriever.os.path.exists", return_value=False)
    def test_load_vectorstore_raises_if_no_index(self, _):
        from app.rag.retriever import load_vectorstore
        with pytest.raises(FileNotFoundError, match="FAISS index not found"):
            load_vectorstore()

    @patch("app.rag.retriever.FAISS")
    @patch("app.rag.retriever.os.path.exists", return_value=True)
    def test_retrieve_chunks_returns_documents(self, _, mock_faiss):
        from app.rag.retriever import retrieve_chunks

        mock_doc = Document(page_content="LangGraph is great.", metadata={"source": "doc.pdf", "page": 1})
        mock_retriever = MagicMock()
        mock_retriever.invoke.return_value = [mock_doc]
        mock_faiss.load_local.return_value.as_retriever.return_value = mock_retriever

        results = retrieve_chunks("What is LangGraph?", k=1)

        assert len(results) == 1
        assert results[0].page_content == "LangGraph is great."

    def test_format_context_numbered_output(self):
        from app.rag.retriever import format_context

        docs = [
            Document(page_content="First chunk.",  metadata={"source": "a.pdf", "page": 1}),
            Document(page_content="Second chunk.", metadata={"source": "b.pdf", "page": 2}),
        ]
        result = format_context(docs)

        assert "[1]" in result
        assert "[2]" in result
        assert "First chunk." in result
        assert "Second chunk." in result


# ══════════════════════════════════════════════════════════════════════════════
# test rag_chain
# ══════════════════════════════════════════════════════════════════════════════

class TestRagChain:

    @patch("app.rag.rag_chain.retrieve_chunks", return_value=[])
    def test_run_rag_chain_no_docs_returns_fallback(self, _):
        from app.rag.rag_chain import run_rag_chain

        result = run_rag_chain("anything")

        assert "couldn't find" in result["answer"].lower()
        assert result["sources"] == []

    @patch("app.rag.rag_chain.llm")
    @patch("app.rag.rag_chain.retrieve_chunks")
    def test_run_rag_chain_with_docs_returns_answer(self, mock_retrieve, mock_llm):
        from app.rag.rag_chain import run_rag_chain

        mock_doc = Document(
            page_content="LangGraph builds stateful agents.",
            metadata={"source": "doc.pdf", "page": 1}
        )
        mock_retrieve.return_value = [mock_doc]

        mock_response         = MagicMock()
        mock_response.content = "LangGraph is used for stateful agents."
        mock_llm.invoke.return_value = mock_response

        result = run_rag_chain("What is LangGraph?")

        assert result["answer"] == "LangGraph is used for stateful agents."
        assert "doc.pdf" in result["sources"]