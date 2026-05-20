import os

import torch
import yaml

from src.tts.exceptions import TTSProcessingError

YML_URL = "https://raw.githubusercontent.com/snakers4/silero-models/refs/heads/master/models.yml"


class SileroTTSModelProvider:
    """Manages local Silero .pt model files."""

    def __init__(self, models_dir: str = ".models/silero"):
        self._models_dir = models_dir

    def get_model_path(self, language: str, model_name: str) -> str:
        """Return the local path to a model .pt file.

        Downloads the file if it does not exist locally.
        Raises TTSProcessingError on failure.
        """
        import urllib.request

        lang_dir = os.path.join(self._models_dir, language)
        os.makedirs(lang_dir, exist_ok=True)
        model_path = os.path.join(lang_dir, f"{model_name}.pt")

        if os.path.isfile(model_path):
            return model_path

        yml_path = os.path.join(self._models_dir, "models.yml")
        if not os.path.isfile(yml_path):
            urllib.request.urlretrieve(YML_URL, yml_path)

        try:
            with open(yml_path) as f:
                registry = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise TTSProcessingError(
                f"Failed to parse models.yml: {e}. "
                "Delete .models/silero/models.yml to force a fresh download."
            ) from e

        tts_models = registry.get("tts_models", {})
        lang_models = tts_models.get(language, {})
        model_entry = lang_models.get(model_name, {})
        package_url = model_entry.get("latest", {}).get("package")

        if not package_url:
            raise TTSProcessingError(
                f"Model '{model_name}' for language '{language}' not found in models.yml. "
                "Delete .models/silero/models.yml to force a fresh download."
            )

        try:
            torch.hub.download_url_to_file(package_url, model_path)
        except Exception as e:
            if os.path.isfile(model_path):
                os.remove(model_path)
            raise TTSProcessingError(
                f"Failed to download model '{model_name}' for language '{language}'."
            ) from e

        return model_path
