import os

VACE_ENABLED = os.getenv("VACE_ENABLED", "0") == "1"
VACE_CLI = os.getenv("VACE_CLI", "python vace_pipeline.py")  # placeholder
ROOT_MODELS = os.getenv("ROOT_MODELS", "./models")


