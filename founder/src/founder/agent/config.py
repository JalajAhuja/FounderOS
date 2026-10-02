import os

from dotenv import load_dotenv


load_dotenv()


# ============================================================
# OPENAI
# ============================================================

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)

AGENT_MODEL = os.getenv(
    "AGENT_MODEL",
    "gpt-4o-mini",
)


# ============================================================
# AGENT LOOP LIMITS
# ============================================================

MAX_RETRIEVAL_ROUNDS = 2

DEFAULT_TOP_K = 8
