import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.testclient import TestClient
from groq import APIConnectionError, APIStatusError
from httpx import Request, Response

from main import app, generate_answer, get_allowed_origins


class ChatApiTests(unittest.TestCase):
    def test_allowed_origins_include_configured_frontends(self):
        with patch.dict(
            os.environ,
            {
                "FRONTEND_URL": "https://portfolio-ai.example/",
                "FRONTEND_ORIGINS": (
                    " https://preview-one.example/ ,"
                    "https://preview-two.example"
                ),
            },
        ):
            origins = get_allowed_origins()

        self.assertIn("https://portfolio-ai.example", origins)
        self.assertIn("https://preview-one.example", origins)
        self.assertIn("https://preview-two.example", origins)
        self.assertNotIn("*", origins)

    def test_new_vercel_origin_passes_cors_preflight(self):
        with TestClient(app) as client:
            response = client.options(
                "/upload-resume",
                headers={
                    "Origin": "https://portfolio-ai-multi-agent-rag.vercel.app",
                    "Access-Control-Request-Method": "POST",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["access-control-allow-origin"],
            "https://portfolio-ai-multi-agent-rag.vercel.app",
        )

    def test_uploaded_resume_can_be_used_for_chat(self):
        with tempfile.TemporaryDirectory() as upload_dir:
            with (
                patch("main.UPLOAD_DIR", Path(upload_dir)),
                patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}),
                patch("main.read_pdf", return_value="PROJECTS\nBuilt an assistant"),
                patch(
                    "main.retrieve_resume_chunks",
                    return_value=[{"section": "Projects", "content": "Built an assistant"}],
                ),
                patch("main.Groq") as groq_client,
            ):
                groq_client.return_value.chat.completions.create.return_value = (
                    SimpleNamespace(
                        choices=[
                            SimpleNamespace(
                                message=SimpleNamespace(content="The candidate built an assistant.")
                            )
                        ]
                    )
                )
                with TestClient(app) as client:
                    upload_response = client.post(
                        "/upload-resume",
                        files={"file": ("resume.pdf", b"%PDF-1.4 test", "application/pdf")},
                    )
                    self.assertEqual(upload_response.status_code, 200)

                    chat_response = client.post(
                        "/chat",
                        json={
                            "question": "Describe the project.",
                            "resume_file": upload_response.json()["filename"],
                        },
                    )

        self.assertEqual(chat_response.status_code, 200)
        self.assertEqual(chat_response.json()["agent"], "project")
        self.assertEqual(chat_response.json()["answer"], "The candidate built an assistant.")
        self.assertEqual(len(chat_response.json()["sources"]), 1)

    def test_provider_authentication_error_is_actionable(self):
        error = APIStatusError(
            "Unauthorized",
            response=Response(401, request=Request("POST", "https://api.groq.com")),
            body={"error": "Unauthorized"},
        )
        self._assert_provider_error(
            error,
            "AI provider authentication failed. Check GROQ_API_KEY in the backend environment.",
        )

    def test_provider_rate_limit_error_is_actionable(self):
        error = APIStatusError(
            "Rate limited",
            response=Response(429, request=Request("POST", "https://api.groq.com")),
            body={"error": "Rate limited"},
        )
        self._assert_provider_error(
            error,
            "The AI provider rate limit or quota was reached. Check your Groq account limits and try again.",
        )

    def test_provider_connection_error_is_distinguished(self):
        error = APIConnectionError(request=Request("POST", "https://api.groq.com"))
        self._assert_provider_error(
            error,
            "Could not reach the AI provider. Check backend network access and try again.",
        )

    def _assert_provider_error(self, error, expected_detail):
        with (
            patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}),
            patch("main.Groq") as groq_client,
        ):
            groq_client.return_value.chat.completions.create.side_effect = error
            with self.assertRaises(HTTPException) as raised:
                generate_answer("question", "recruiter", [])

        self.assertEqual(raised.exception.status_code, 502)
        self.assertEqual(raised.exception.detail, expected_detail)


if __name__ == "__main__":
    unittest.main()
