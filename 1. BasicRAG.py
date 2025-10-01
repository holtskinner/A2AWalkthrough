from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig, Part

load_dotenv()

with open("data/gold-hospital-and-premium-extras.pdf", "rb") as f:
    pdf_bytes = f.read()

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=[
        Part.from_uri(
            file_uri="https://mybenefits.wageworks.com/media/docs/CXWW/39068/Google%20IH%20GHIP%20SBC%20Final.pdf"
        ),
        "How much would I pay for mental health therapy?",
    ],
    config=GenerateContentConfig(
        system_instruction="You are an expert insurance agent designed to assist with coverage queries. Use the provided documents to answer questions about insurance policies. If the information is not available in the documents, respond with 'I don't know'",
    ),
)

print(response.text)
