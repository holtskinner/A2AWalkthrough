import base64
import os

from anthropic import AnthropicVertex
from anthropic.types import (
    Base64PDFSourceParam,
    DocumentBlockParam,
    MessageParam,
    TextBlockParam,
)
from dotenv import load_dotenv

load_dotenv()

client = AnthropicVertex(
    project_id=os.environ.get("GOOGLE_CLOUD_PROJECT"),
    region="us-east5",
)

with open("./data/2026AnthemgHIPSBC.pdf", "rb") as file:
    pdf_data = base64.standard_b64encode(file.read()).decode("utf-8")

prompt = "How much would I pay for mental health therapy?"

response = client.messages.create(
    model="claude-3-5-haiku@20241022",
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
                        data=pdf_data,
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

print(response.content[0].text)
