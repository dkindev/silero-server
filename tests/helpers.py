import hashlib

import yaml

from src.tts.models import Model, Voice


def hash_models_yml(yml_path: str) -> str:
    """Compute SHA256 hex digest of a models.yml file."""
    hasher = hashlib.sha256()
    with open(yml_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest().lower()


def make_models_dir(tmp_path, sample_rates=None, model_name="v5_5_ru", language="ru"):
    """Create a models directory with pre-populated models.yml and .pt files."""
    if sample_rates is None:
        sample_rates = [48000]
    rates_str = ", ".join(str(r) for r in sample_rates)
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    yml = (
        f"tts_models:\n  {language}:\n    {model_name}:\n"
        f"      latest:\n"
        f"        package: 'http://x'\n"
        f"        sample_rate: [{rates_str}]\n"
    )
    (models_dir / "models.yml").write_text(yml)
    lang_dir = models_dir / language
    lang_dir.mkdir()
    (lang_dir / f"{model_name}.pt").write_bytes(b"fake model")
    return str(models_dir)


def make_config_file(tmp_path, models=None):
    """Create a temp config file with merged structure."""
    config_yml = tmp_path / "config.yml"
    config_data = {"models": models or {}}
    config_yml.write_text(yaml.dump(config_data))
    return str(config_yml)


def make_voice(*, voice_id, name, speaker=None, model="v5_5_ru", locale="ru_RU"):
    return Voice(
        id=voice_id,
        name=name,
        speaker=speaker or name,
        model=model,
        locale=locale,
    )


def make_model(name="v5_5_ru", language="ru", warmup=False, enabled=True):
    return Model(name=name, language=language, warmup=warmup, enabled=enabled)


def make_merged_yaml(tmp_path, models_data: dict) -> str:
    """Write a merged-structure config YAML and return its path."""
    config_yml = tmp_path / "config.yml"
    config_yml.write_text(yaml.dump({"models": models_data}))
    return str(config_yml)


async def collect_chunks(engine, text, voice_id, input_type="TEXT"):
    """Collect all chunks from synthesize_pcm_chunks into a list."""
    return [chunk async for chunk in engine.synthesize_pcm_chunks(text, voice_id, input_type)]
