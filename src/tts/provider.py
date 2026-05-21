import os

import torch
import yaml

from src.tts.exceptions import TTSEngineError

MODELS_YML_URL = (
    "https://raw.githubusercontent.com/snakers4/silero-models/refs/heads/master/models.yml"
)


class SileroTTSModelProvider:
    """Manages local Silero .pt model files."""

    def __init__(self, models_dir: str = ".models/silero"):
        self._models_dir = models_dir

    def get_model(self, language: str, model_name: str) -> tuple[str, list[int]]:
        """Return the local path to a model .pt file and its supported sample rates.

        Downloads the file if it does not exist locally.
        Raises TTSEngineError on failure.
        """
        import urllib.request

        lang_dir = os.path.join(self._models_dir, language)
        os.makedirs(lang_dir, exist_ok=True)

        yml_path = os.path.join(self._models_dir, "models.yml")
        if not os.path.isfile(yml_path):
            urllib.request.urlretrieve(MODELS_YML_URL, yml_path)

        try:
            with open(yml_path) as f:
                registry = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise TTSEngineError(
                f"Failed to parse models.yml: {e}. Delete '{yml_path}' to force a fresh download."
            ) from e

        tts_models = registry.get("tts_models", {})
        lang_models = tts_models.get(language, {})
        model_entry = lang_models.get(model_name, {})
        sample_rates = model_entry.get("latest", {}).get("sample_rate", [])

        model_path = os.path.join(lang_dir, f"{model_name}.pt")
        if os.path.isfile(model_path):
            return model_path, sample_rates

        package_url = model_entry.get("latest", {}).get("package")
        if not package_url:
            raise TTSEngineError(
                f"Model '{model_name}' for language '{language}' not found in configuration file. "
                f"Delete '{yml_path}' to force a fresh download."
            )

        try:
            torch.hub.download_url_to_file(package_url, model_path)
        except Exception as e:
            if os.path.isfile(model_path):
                os.remove(model_path)
            raise TTSEngineError(
                f"Failed to download model '{model_name}' for language '{language}'."
            ) from e

        return model_path, sample_rates
