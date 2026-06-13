import pytest

from src.tts.models import Locale, Model, TTSConfigModel, Voice


class TestSileroTTSYamlConfigStorageInit:
    """Tests for SileroTTSYamlConfigStorage initialization."""

    def test_init_accepts_config_model(self):
        """Should accept TTSConfigModel and expose has_locale."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_model = TTSConfigModel(
            models=[Model(name="v5_5_ru", language="ru")],
            locales=[Locale(name="ru_RU")],
            voices=[
                Voice(
                    name="silero-v5_5_ru-aidar",
                    speaker="aidar",
                    model="v5_5_ru",
                    gender="male",
                    locale="ru_RU",
                )
            ],
        )

        storage = SileroTTSYamlConfigStorage(config_model)

        assert storage.has_locale("ru_RU") is True
        assert storage.has_locale("de_DE") is False


class TestHasVoice:
    """Tests for has_voice() method."""

    def test_has_voice_true_for_configured_voice(self):
        """has_voice should return True for a voice that exists for the locale."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_model = TTSConfigModel(
            models=[Model(name="v5_5_ru", language="ru")],
            locales=[Locale(name="ru_RU")],
            voices=[
                Voice(
                    name="silero-v5_5_ru-aidar",
                    speaker="aidar",
                    model="v5_5_ru",
                    gender="male",
                    locale="ru_RU",
                )
            ],
        )

        storage = SileroTTSYamlConfigStorage(config_model)

        assert storage.has_voice("ru_RU", "silero-v5_5_ru-aidar") is True

    def test_has_voice_false_for_missing_locale(self):
        """has_voice should return False if the locale doesn't exist."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_model = TTSConfigModel(models=[], locales=[], voices=[])
        storage = SileroTTSYamlConfigStorage(config_model)

        assert storage.has_voice("ru_RU", "silero-v5_5_ru-aidar") is False

    def test_has_voice_false_for_missing_voice(self):
        """has_voice should return False if the voice doesn't exist for the locale."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_model = TTSConfigModel(
            models=[Model(name="v5_5_ru", language="ru")],
            locales=[Locale(name="ru_RU")],
            voices=[],
        )
        storage = SileroTTSYamlConfigStorage(config_model)

        assert storage.has_voice("ru_RU", "silero-v5_5_ru-aidar") is False


class TestGetLocales:
    """Tests for get_locales() method."""

    def test_get_locales_returns_list(self):
        """get_locales should return a list of Locale objects."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_model = TTSConfigModel(models=[], locales=[], voices=[])
        storage = SileroTTSYamlConfigStorage(config_model)

        result = storage.get_locales()
        assert isinstance(result, list)

    def test_get_locales_only_returns_locales_with_enabled_voices(self):
        """get_locales should only return locales that have at least one voice on an enabled model."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_model = TTSConfigModel(
            models=[Model(name="v5_5_ru", language="ru")],
            locales=[Locale(name="ru_RU"), Locale(name="de_DE")],
            voices=[
                Voice(
                    name="aidar",
                    speaker="aidar",
                    model="v5_5_ru",
                    gender="male",
                    locale="ru_RU",
                ),
            ],
        )
        storage = SileroTTSYamlConfigStorage(config_model)

        result = storage.get_locales()
        assert any(locale.name == "ru_RU" for locale in result)
        assert not any(locale.name == "de_DE" for locale in result)
        assert len(result) == 1


class TestGetVoices:
    """Tests for get_voices() method."""

    def test_get_voices_returns_list(self):
        """get_voices should return a list of Voice objects."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_model = TTSConfigModel(models=[], locales=[], voices=[])
        storage = SileroTTSYamlConfigStorage(config_model)

        result = storage.get_voices()
        assert isinstance(result, list)

    def test_get_voices_returns_voice_objects(self):
        """get_voices should return list of Voice objects."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_model = TTSConfigModel(
            models=[Model(name="v5_5_ru", language="ru")],
            locales=[Locale(name="ru_RU")],
            voices=[
                Voice(
                    name="silero-v5_5_ru-aidar",
                    speaker="aidar",
                    model="v5_5_ru",
                    gender="male",
                    locale="ru_RU",
                )
            ],
        )
        storage = SileroTTSYamlConfigStorage(config_model)

        result = storage.get_voices()
        assert len(result) == 1
        assert result[0].name == "silero-v5_5_ru-aidar"
        assert result[0].gender == "male"
        assert result[0].locale == "ru_RU"

    def test_get_voices_includes_all_voices(self):
        """get_voices should include all voices."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_model = TTSConfigModel(
            models=[Model(name="v5_5_ru", language="ru")],
            locales=[Locale(name="ru_RU")],
            voices=[
                Voice(
                    name="silero-v5_5_ru-aidar",
                    speaker="aidar",
                    model="v5_5_ru",
                    gender="male",
                    locale="ru_RU",
                ),
                Voice(
                    name="silero-v5_5_ru-baya",
                    speaker="baya",
                    model="v5_5_ru",
                    gender="female",
                    locale="ru_RU",
                ),
            ],
        )
        storage = SileroTTSYamlConfigStorage(config_model)

        result = storage.get_voices()
        assert len(result) == 2
        assert result[0].name == "silero-v5_5_ru-aidar"
        assert result[1].name == "silero-v5_5_ru-baya"

    def test_get_voices_from_all_locales(self):
        """get_voices should include voices from all locales."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_model = TTSConfigModel(
            models=[Model(name="v5_5_ru", language="ru"), Model(name="v3_en", language="en")],
            locales=[Locale(name="ru_RU"), Locale(name="en_US")],
            voices=[
                Voice(
                    name="silero-v5_5_ru-aidar",
                    speaker="aidar",
                    model="v5_5_ru",
                    gender="male",
                    locale="ru_RU",
                ),
                Voice(
                    name="silero-v3_en-en_0",
                    speaker="en_0",
                    model="v3_en",
                    gender="male",
                    locale="en_US",
                ),
            ],
        )
        storage = SileroTTSYamlConfigStorage(config_model)

        result = storage.get_voices()
        assert len(result) == 2


class TestGetVoice:
    """Tests for get_voice() method."""

    def test_get_voice_returns_correct_config(self):
        """get_voice should return Voice for the given locale and voice."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_model = TTSConfigModel(
            models=[Model(name="v5_5_ru", language="ru")],
            locales=[Locale(name="ru_RU")],
            voices=[
                Voice(
                    name="silero-v5_5_ru-aidar",
                    speaker="aidar",
                    model="v5_5_ru",
                    gender="male",
                    locale="ru_RU",
                )
            ],
        )
        storage = SileroTTSYamlConfigStorage(config_model)

        voice = storage.get_voice("ru_RU", "silero-v5_5_ru-aidar")
        assert voice.speaker == "aidar"
        assert voice.model == "v5_5_ru"
        assert voice.gender == "male"


class TestYamlConstructor:
    """Tests for constructing from a YAML file path."""

    def test_loads_config_from_yaml_path(self, tmp_path):
        """Should load config from a YAML file path."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
locales:
  ru_RU:
    voices:
      silero-v5_5_ru-aidar:
        speaker: aidar
        model: v5_5_ru
        gender: male
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))

        assert storage.has_locale("ru_RU") is True
        assert storage.has_voice("ru_RU", "silero-v5_5_ru-aidar") is True

    def test_loaded_voices_have_voice_configs(self, tmp_path):
        """get_voices should return Voice objects after loading from YAML."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
locales:
  ru_RU:
    voices:
      silero-v5_5_ru-aidar:
        speaker: aidar
        model: v5_5_ru
        gender: male
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))

        voices = storage.get_voices()
        assert len(voices) == 1
        assert voices[0].name == "silero-v5_5_ru-aidar"
        assert voices[0].gender == "male"
        assert voices[0].locale == "ru_RU"

    def test_missing_speaker_defaults_to_voice_name(self, tmp_path):
        """YAML without speaker field should default speaker to voice_name."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
locales:
  ru_RU:
    voices:
      silero-v5_5_ru-aidar:
        model: v5_5_ru
        gender: male
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))
        voice = storage.get_voice("ru_RU", "silero-v5_5_ru-aidar")
        assert voice.speaker == "silero-v5_5_ru-aidar"

    def test_empty_speaker_defaults_to_voice_name(self, tmp_path):
        """YAML with speaker: '' should default speaker to voice_name."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
locales:
  ru_RU:
    voices:
      silero-v5_5_ru-aidar:
        speaker: ""
        model: v5_5_ru
        gender: male
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))
        voice = storage.get_voice("ru_RU", "silero-v5_5_ru-aidar")
        assert voice.speaker == "silero-v5_5_ru-aidar"


class TestEmptyConfig:
    """Tests for empty/minimal configs."""

    def test_empty_config(self):
        """Should handle empty config with no locales or models."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_model = TTSConfigModel(models=[], locales=[], voices=[])
        storage = SileroTTSYamlConfigStorage(config_model)

        assert storage.get_locales() == []
        assert storage.get_voices() == []
        assert storage.has_locale("anything") is False

    def test_empty_config_from_yaml(self, tmp_path):
        """Should load and handle empty YAML config."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_yml = tmp_path / "empty.yml"
        config_yml.write_text("")

        storage = SileroTTSYamlConfigStorage(str(config_yml))

        assert storage.get_locales() == []
        assert storage.get_voices() == []


class TestYamlEnabledField:
    """Tests for parsing enabled field from YAML config."""

    def test_yaml_enabled_false_disables_model(self, tmp_path):
        """YAML with enabled: false should disable the model."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
    enabled: false
locales:
  ru_RU:
    voices:
      silero-v5_5_ru-aidar:
        speaker: aidar
        model: v5_5_ru
        gender: male
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))

        assert storage.has_locale("ru_RU") is False
        assert storage.has_voice("ru_RU", "silero-v5_5_ru-aidar") is False

    def test_yaml_without_enabled_defaults_to_enabled(self, tmp_path):
        """YAML without enabled field should keep the model enabled."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
locales:
  ru_RU:
    voices:
      silero-v5_5_ru-aidar:
        speaker: aidar
        model: v5_5_ru
        gender: male
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))

        assert storage.has_locale("ru_RU") is True
        assert storage.has_voice("ru_RU", "silero-v5_5_ru-aidar") is True

    def test_yaml_enabled_true_explicitly_enables_model(self, tmp_path):
        """YAML with enabled: true should keep the model enabled."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
    enabled: true
locales:
  ru_RU:
    voices:
      silero-v5_5_ru-aidar:
        speaker: aidar
        model: v5_5_ru
        gender: male
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))

        assert storage.has_locale("ru_RU") is True
        assert storage.has_voice("ru_RU", "silero-v5_5_ru-aidar") is True

    def test_yaml_mixed_enabled_and_disabled(self, tmp_path):
        """YAML with mixed enabled/disabled models filters correctly."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
    enabled: false
  v3_en:
    language: en
    enabled: true
locales:
  ru_RU:
    voices:
      silero-v5_5_ru-aidar:
        speaker: aidar
        model: v5_5_ru
        gender: male
  en_US:
    voices:
      silero-v3_en-en_0:
        speaker: en_0
        model: v3_en
        gender: male
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))

        assert storage.has_locale("ru_RU") is False
        assert storage.has_locale("en_US") is True
        assert storage.has_voice("en_US", "silero-v3_en-en_0") is True

        voices = storage.get_voices()
        assert not any(voice.locale == "ru_RU" for voice in voices)
        assert any(voice.locale == "en_US" for voice in voices)
        assert any(voice.name == "silero-v3_en-en_0" for voice in voices)


class TestGetModelInfo:
    """Tests for get_model_info() method."""

    def test_get_model_info_returns_correct_model(self):
        """get_model_info should return Model for the given model name."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_model = TTSConfigModel(
            models=[Model(name="v5_5_ru", language="ru")],
            locales=[],
            voices=[],
        )
        storage = SileroTTSYamlConfigStorage(config_model)

        m = storage.get_model_info("v5_5_ru")
        assert m.language == "ru"


class TestGetModels:
    def test_get_models_returns_all_enabled_models(self):
        """get_models() returns dict of all enabled model names to Model objects."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_model = TTSConfigModel(
            models=[
                Model(name="v5_5_ru", language="ru", warmup=True),
                Model(name="v3_en", language="en"),
            ],
            locales=[Locale(name="ru_RU")],
            voices=[
                Voice(
                    name="silero-v5_5_ru-aidar",
                    speaker="aidar",
                    model="v5_5_ru",
                    gender="male",
                    locale="ru_RU",
                )
            ],
        )

        storage = SileroTTSYamlConfigStorage(config_model)
        result = storage.get_models()

        assert isinstance(result, dict)
        assert "v5_5_ru" in result
        assert result["v5_5_ru"].warmup is True
        assert "v3_en" in result
        assert result["v3_en"].warmup is False


class TestYamlWarmupField:
    """Tests for parsing warmup field from YAML config."""

    def test_yaml_warmup_true_sets_warmup_on_model(self, tmp_path):
        """YAML with warmup: true should set warmup=True on Model."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
    warmup: true
locales:
  ru_RU:
    voices:
      silero-v5_5_ru-aidar:
        speaker: aidar
        model: v5_5_ru
        gender: male
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))
        models = storage.get_models()

        assert models["v5_5_ru"].warmup is True

    def test_yaml_without_warmup_defaults_to_false(self, tmp_path):
        """YAML without warmup field should default to False."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
locales:
  ru_RU:
    voices:
      silero-v5_5_ru-aidar:
        speaker: aidar
        model: v5_5_ru
        gender: male
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))
        models = storage.get_models()

        assert models["v5_5_ru"].warmup is False


class TestYamlHashPrefixField:
    """Tests for parsing hash_prefix field from YAML config."""

    def test_yaml_hash_prefix_sets_hash_prefix_on_model(self, tmp_path):
        """YAML with hash_prefix should set hash_prefix on Model."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
    hash_prefix: "a1b2c3d4"
locales:
  ru_RU:
    voices:
      silero-v5_5_ru-aidar:
        speaker: aidar
        model: v5_5_ru
        gender: male
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))
        models = storage.get_models()

        assert models["v5_5_ru"].hash_prefix == "a1b2c3d4"

    def test_yaml_without_hash_prefix_defaults_to_none(self, tmp_path):
        """YAML without hash_prefix should default to None."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
locales:
  ru_RU:
    voices:
      silero-v5_5_ru-aidar:
        speaker: aidar
        model: v5_5_ru
        gender: male
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))
        models = storage.get_models()

        assert models["v5_5_ru"].hash_prefix is None

    def test_yaml_empty_hash_prefix_defaults_to_none(self, tmp_path):
        """YAML with empty hash_prefix should default to None."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
    hash_prefix: ""
locales:
  ru_RU:
    voices:
      silero-v5_5_ru-aidar:
        speaker: aidar
        model: v5_5_ru
        gender: male
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))
        models = storage.get_models()

        assert models["v5_5_ru"].hash_prefix is None


class TestDisabledModel:
    """Tests for model disabling via enabled=False on Model."""

    def test_disabled_model_voices_excluded_from_get_voices(self):
        """get_voices should exclude voices that reference a disabled model."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_model = TTSConfigModel(
            models=[
                Model(name="v5_5_ru", language="ru", enabled=False),
                Model(name="v3_en", language="en", enabled=True),
            ],
            locales=[Locale(name="ru_RU"), Locale(name="en_US")],
            voices=[
                Voice(
                    name="silero-v5_5_ru-aidar",
                    speaker="aidar",
                    model="v5_5_ru",
                    gender="male",
                    locale="ru_RU",
                ),
                Voice(
                    name="silero-v3_en-en_0",
                    speaker="en_0",
                    model="v3_en",
                    gender="male",
                    locale="en_US",
                ),
            ],
        )

        storage = SileroTTSYamlConfigStorage(config_model)

        result = storage.get_voices()
        assert not any(voice.locale == "ru_RU" for voice in result)
        assert any(voice.locale == "en_US" for voice in result)
        assert any(voice.name == "silero-v3_en-en_0" for voice in result)

    def test_disabled_model_orphaned_locale_excluded_from_get_locales(self):
        """get_locales should exclude locales where all voices reference disabled models."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_model = TTSConfigModel(
            models=[
                Model(name="v5_5_ru", language="ru", enabled=False),
                Model(name="v3_en", language="en", enabled=True),
            ],
            locales=[Locale(name="ru_RU"), Locale(name="en_US")],
            voices=[
                Voice(
                    name="silero-v5_5_ru-aidar",
                    speaker="aidar",
                    model="v5_5_ru",
                    gender="male",
                    locale="ru_RU",
                ),
                Voice(
                    name="silero-v3_en-en_0",
                    speaker="en_0",
                    model="v3_en",
                    gender="male",
                    locale="en_US",
                ),
            ],
        )

        storage = SileroTTSYamlConfigStorage(config_model)

        result = storage.get_locales()
        assert not any(locale.name == "ru_RU" for locale in result)
        assert any(locale.name == "en_US" for locale in result)

    def test_disabled_model_has_voice_false(self):
        """has_voice should return False for voices that reference a disabled model."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_model = TTSConfigModel(
            models=[
                Model(name="v5_5_ru", language="ru", enabled=False),
                Model(name="v3_en", language="en", enabled=True),
            ],
            locales=[Locale(name="ru_RU"), Locale(name="en_US")],
            voices=[
                Voice(
                    name="silero-v5_5_ru-aidar",
                    speaker="aidar",
                    model="v5_5_ru",
                    gender="male",
                    locale="ru_RU",
                ),
                Voice(
                    name="silero-v3_en-en_0",
                    speaker="en_0",
                    model="v3_en",
                    gender="male",
                    locale="en_US",
                ),
            ],
        )

        storage = SileroTTSYamlConfigStorage(config_model)

        assert storage.has_voice("ru_RU", "silero-v5_5_ru-aidar") is False
        assert storage.has_voice("en_US", "silero-v3_en-en_0") is True

    def test_disabled_model_has_locale_false(self):
        """has_locale should return False for locales with only disabled-model voices."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_model = TTSConfigModel(
            models=[
                Model(name="v5_5_ru", language="ru", enabled=False),
                Model(name="v3_en", language="en", enabled=True),
            ],
            locales=[Locale(name="ru_RU"), Locale(name="en_US")],
            voices=[
                Voice(
                    name="silero-v5_5_ru-aidar",
                    speaker="aidar",
                    model="v5_5_ru",
                    gender="male",
                    locale="ru_RU",
                ),
                Voice(
                    name="silero-v3_en-en_0",
                    speaker="en_0",
                    model="v3_en",
                    gender="male",
                    locale="en_US",
                ),
            ],
        )

        storage = SileroTTSYamlConfigStorage(config_model)

        assert storage.has_locale("ru_RU") is False
        assert storage.has_locale("en_US") is True

    def test_disabled_model_get_model_info_raises_key_error(self):
        """get_model_info should raise KeyError for a disabled model."""
        from src.tts.config_storage import SileroTTSYamlConfigStorage

        config_model = TTSConfigModel(
            models=[
                Model(name="v5_5_ru", language="ru", enabled=False),
            ],
            locales=[],
            voices=[],
        )

        storage = SileroTTSYamlConfigStorage(config_model)

        with pytest.raises(KeyError):
            storage.get_model_info("v5_5_ru")
