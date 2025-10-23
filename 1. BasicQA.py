import base64
import os
from pathlib import Path

from anthropic import AnthropicVertex
from anthropic.types import (
    Base64PDFSourceParam,
    DocumentBlockParam,
    MessageParam,
    TextBlockParam,
)
from dotenv import load_dotenv


class PolicyAgent:

    def __init__(self):
        load_dotenv()
        self.client = AnthropicVertex(
            project_id=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            region="global",
        )
        with Path("./data/2026AnthemgHIPSBC.pdf").open("rb") as file:
            self.pdf_data = base64.standard_b64encode(file.read()).decode("utf-8")

    def answer_query(self, prompt: str) -> str:
        response = self.client.messages.create(
            model="claude-haiku-4-5@20251001",
            max_tokens=1024,
            system="You are an expert insurance agent designed to assist with coverage queries. Use the provided documents to answer questions about insurance policies. If the information is not available in the documents, respond with 'I don't know'",
            messages=[
                MessageParam(
                    role="user",
                    content=[
                        DocumentBlockParam(
                            type="document",
                            source=Base64PDFSourceParam(
                                type="base64",
                                media_type="application/pdf",
                                data=self.pdf_data,
                            ),
                        ),
                        TextBlockParam(
                            type="text",
                            text=prompt,
                        ),
                    ],
                )
            ],
        )
        return response.content[0].text


if __name__ == "__main__":
    print("Running Health Insurance Policy Agent")
    agent = PolicyAgent()
    prompt = "How much would I pay for mental health therapy?"

    response = agent.answer_query(prompt)
    print(response)
