from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig, Part

load_dotenv()

with open("data/gold-hospital-and-premium-extras.pdf", "rb") as f:
    pdf_bytes = f.read()

client = genai.Client()

with open("./data/2026AnthemgHIPSBC.pdf", "rb") as file:
    pdf_bytes = file.read()

response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=[
        Part.from_bytes(
            data=pdf_bytes,
            mime_type="application/pdf",
        ),
        "How much would I pay for mental health therapy?",
    ],
    config=GenerateContentConfig(
        system_instruction="You are an expert insurance agent designed to assist with coverage queries. Use the provided documents to answer questions about insurance policies. If the information is not available in the documents, respond with 'I don't know'",
    ),
)

print(response.text)
