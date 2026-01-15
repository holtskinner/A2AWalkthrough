import base64
from pathlib import Path

import litellm

from helpers import setup_env


class PolicyAgent:
    def __init__(self) -> None:
        setup_env()
        with Path("data/2026AnthemgHIPSBC.pdf").open("rb") as file:
            self.pdf_data = base64.standard_b64encode(file.read()).decode("utf-8")

    def answer_query(self, prompt: str) -> str:
        response = litellm.completion(
            model="gemini/gemini-3-flash-preview",
            reasoning_effort="minimal",
            max_tokens=1000,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert insurance agent designed to assist with coverage queries. Use the provided documents to answer questions about insurance policies. If the information is not available in the documents, respond with 'I don't know'",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:application/pdf;base64,{self.pdf_data}"
                            },
                        },
                    ],
                },
            ],
        )

        return response.choices[0].message.content.replace("$", r"\$")
