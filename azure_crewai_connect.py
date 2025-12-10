# azure_crewai_connect.py
import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from crewai import Agent, Task, Crew, Process
from crewai.llms.base_llm import BaseLLM
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)

# 👇 Define a CrewAI-compatible LLM provider

class AzureCrewAILLM(BaseLLM):
    def __init__(self):
        self.client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
        )
        self.deployment = deployment
        self._token_usage = {}  # ✅ required by CrewAI for summary

    def call(self, prompt, **kwargs) -> str:
        # CrewAI sometimes passes a list of strings → flatten them
        if isinstance(prompt, list):
            prompt = "\n".join(str(p) for p in prompt)

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": str(prompt)}
                    ],
                }
            ],
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=4096,  # Force 4096 tokens to ensure complete JSON responses
        )

        # --- extract token usage if present (Azure sometimes omits this) ---
        try:
            usage = getattr(response, "usage", None)
            if usage:
                self._token_usage = {
                    "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(usage, "completion_tokens", 0),
                    "total_tokens": getattr(usage, "total_tokens", 0),
                }
        except Exception:
            self._token_usage = {}

        # --- handle message content ---
        msg = response.choices[0].message
        content = msg.content
        if isinstance(content, list):
            texts = [block.text for block in content if hasattr(block, "text")]
            return "\n".join(texts)
        return str(content)
