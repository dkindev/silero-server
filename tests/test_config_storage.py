from src.tts.config_storage import SileroTTSYamlConfigStorage
from src.tts.models import Model, TTSConfigModel, Voice


class TestSileroTTSYamlConfigStorageInit:
    """Tests for SileroTTSYamlConfigStorage initialization."""

    def test_init_accepts_config_model(self):
        """Should accept TTSConfigModel and expose get_voice."""

        config_model = TTSConfigModel(
            models=[Model(name="v5_5_ru", language="ru")],
            voices=[
                Voice(
                    id="ru_RU-v5_5_ru-aidar",
                    name="aidar",
                    speaker="aidar",
                    model="v5_5_ru",
                    locale="ru_RU",
                )
            ],
        )

        storage = SileroTTSYamlConfigStorage(config_model)

        assert storage.get_voice("ru_RU-v5_5_ru-aidar").name == "aidar"


class TestGetVoices:
    """Tests for get_voices() method."""

    def test_get_voices_returns_list(self):
        """get_voices should return a list of Voice objects."""

        config_model = TTSConfigModel(models=[], voices=[])
        storage = SileroTTSYamlConfigStorage(config_model)

        result = storage.get_voices()
        assert isinstance(result, list)

    def test_get_voices_returns_voice_objects(self):
        """get_voices should return list of Voice objects with id field."""

        config_model = TTSConfigModel(
            models=[Model(name="v5_5_ru", language="ru")],
            voices=[
                Voice(
                    id="ru_RU-v5_5_ru-aidar",
                    name="aidar",
                    speaker="aidar",
                    model="v5_5_ru",
                    locale="ru_RU",
                )
            ],
        )
        storage = SileroTTSYamlConfigStorage(config_model)

        result = storage.get_voices()
        assert len(result) == 1
        assert result[0].id == "ru_RU-v5_5_ru-aidar"
        assert result[0].locale == "ru_RU"

    def test_get_voices_includes_all_voices(self):
        """get_voices should include all voices."""

        config_model = TTSConfigModel(
            models=[Model(name="v5_5_ru", language="ru")],
            voices=[
                Voice(
                    id="ru_RU-v5_5_ru-aidar",
                    name="aidar",
                    speaker="aidar",
                    model="v5_5_ru",
                    locale="ru_RU",
                ),
                Voice(
                    id="ru_RU-v5_5_ru-baya",
                    name="baya",
                    speaker="baya",
                    model="v5_5_ru",
                    locale="ru_RU",
                ),
            ],
        )
        storage = SileroTTSYamlConfigStorage(config_model)

        result = storage.get_voices()
        assert len(result) == 2
        assert result[0].name == "aidar"
        assert result[1].name == "baya"

    def test_get_voices_from_all_locales(self):
        """get_voices should include voices from all locales."""

        config_model = TTSConfigModel(
            models=[Model(name="v5_5_ru", language="ru"), Model(name="v3_en", language="en")],
            voices=[
                Voice(
                    id="ru_RU-v5_5_ru-aidar",
                    name="aidar",
                    speaker="aidar",
                    model="v5_5_ru",
                    locale="ru_RU",
                ),
                Voice(
                    id="en_US-v3_en-en_0",
                    name="en_0",
                    speaker="en_0",
                    model="v3_en",
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
        """get_voice should return Voice for the given voice_id."""

        config_model = TTSConfigModel(
            models=[Model(name="v5_5_ru", language="ru")],
            voices=[
                Voice(
                    id="ru_RU-v5_5_ru-aidar",
                    name="aidar",
                    speaker="aidar",
                    model="v5_5_ru",
                    locale="ru_RU",
                )
            ],
        )
        storage = SileroTTSYamlConfigStorage(config_model)

        voice = storage.get_voice("ru_RU-v5_5_ru-aidar")
        assert voice.speaker == "aidar"
        assert voice.model == "v5_5_ru"


class TestYamlConstructor:
    """Tests for constructing from a YAML file path."""

    def test_loads_config_from_yaml_path(self, tmp_path):
        """Should load config from a YAML file path with merged structure."""

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
    locales:
      ru_RU:
        voices:
          - name: aidar
            speaker: aidar
            model: v5_5_ru
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))

        voice = storage.get_voice("ru_RU-v5_5_ru-aidar")
        assert voice.name == "aidar"
        assert voice.speaker == "aidar"
        assert voice.model == "v5_5_ru"

    def test_loaded_voices_have_voice_configs(self, tmp_path):
        """get_voices should return Voice objects with computed id."""

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
    locales:
      ru_RU:
        voices:
          - name: aidar
            speaker: aidar
            model: v5_5_ru
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))

        voices = storage.get_voices()
        assert len(voices) == 1
        assert voices[0].id == "ru_RU-v5_5_ru-aidar"
        assert voices[0].locale == "ru_RU"

    def test_missing_speaker_defaults_to_voice_name(self, tmp_path):
        """YAML without speaker field should default speaker to voice_name."""

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
    locales:
      ru_RU:
        voices:
          - name: aidar
            model: v5_5_ru
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))
        voice = storage.get_voice("ru_RU-v5_5_ru-aidar")
        assert voice.speaker == "aidar"

    def test_empty_speaker_defaults_to_voice_name(self, tmp_path):
        """YAML with speaker: '' should default speaker to voice_name."""

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
    locales:
      ru_RU:
        voices:
          - name: aidar
            speaker: ""
            model: v5_5_ru
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))
        voice = storage.get_voice("ru_RU-v5_5_ru-aidar")
        assert voice.speaker == "aidar"


class TestEmptyConfig:
    """Tests for empty/minimal configs."""

    def test_empty_config(self):
        """Should handle empty config with no locales or models."""

        config_model = TTSConfigModel(models=[], voices=[])
        storage = SileroTTSYamlConfigStorage(config_model)

        assert storage.get_voices() == []

    def test_empty_config_from_yaml(self, tmp_path):
        """Should load and handle empty YAML config."""

        config_yml = tmp_path / "empty.yml"
        config_yml.write_text("")

        storage = SileroTTSYamlConfigStorage(str(config_yml))

        assert storage.get_voices() == []


class TestYamlEnabledField:
    """Tests for parsing enabled field from YAML config."""

    def test_yaml_enabled_false_disables_model(self, tmp_path):
        """YAML with enabled: false should disable the model."""

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
          - name: aidar
            speaker: aidar
            model: v5_5_ru
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))

        assert storage.get_voices() == []

    def test_yaml_without_enabled_defaults_to_enabled(self, tmp_path):
        """YAML without enabled field should keep the model enabled."""

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
    locales:
      ru_RU:
        voices:
          - name: aidar
            speaker: aidar
            model: v5_5_ru
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))

        assert len(storage.get_voices()) == 1

    def test_yaml_enabled_true_explicitly_enables_model(self, tmp_path):
        """YAML with enabled: true should keep the model enabled."""

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
          - name: aidar
            speaker: aidar
            model: v5_5_ru
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))

        assert len(storage.get_voices()) == 1

    def test_yaml_mixed_enabled_and_disabled(self, tmp_path):
        """YAML with mixed enabled/disabled models filters correctly."""

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
          - name: aidar
            speaker: aidar
            model: v5_5_ru
  v3_en:
    language: en
    enabled: true
    locales:
      en_US:
        voices:
          - name: en_0
            speaker: en_0
            model: v3_en
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))

        voices = storage.get_voices()
        assert not any(v.locale == "ru_RU" for v in voices)
        assert any(v.locale == "en_US" for v in voices)
        assert any(v.name == "en_0" for v in voices)


class TestGetModel:
    """Tests for get_model() method."""

    def test_get_model_returns_correct_model(self):
        """get_model should return Model for the given model name."""

        config_model = TTSConfigModel(
            models=[Model(name="v5_5_ru", language="ru")],
            voices=[],
        )
        storage = SileroTTSYamlConfigStorage(config_model)

        m = storage.get_model("v5_5_ru")
        assert m.language == "ru"


class TestGetModels:
    def test_get_models_returns_all_enabled_models(self):
        """get_models() returns list of all enabled Model objects."""

        config_model = TTSConfigModel(
            models=[
                Model(name="v5_5_ru", language="ru", warmup=True),
                Model(name="v3_en", language="en"),
            ],
            voices=[
                Voice(
                    id="ru_RU-v5_5_ru-aidar",
                    name="aidar",
                    speaker="aidar",
                    model="v5_5_ru",
                    locale="ru_RU",
                )
            ],
        )

        storage = SileroTTSYamlConfigStorage(config_model)
        result = storage.get_models()

        model1 = [model for model in result if model.name == "v5_5_ru"]
        model2 = [model for model in result if model.name == "v3_en"]

        assert isinstance(result, list)
        assert len(result) == 2
        assert model1 is not None
        assert model2 is not None


class TestYamlWarmupField:
    """Tests for parsing warmup field from YAML config."""

    def test_yaml_warmup_true_sets_warmup_on_model(self, tmp_path):
        """YAML with warmup: true should set warmup=True on Model."""

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
          - name: aidar
            speaker: aidar
            model: v5_5_ru
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))

        assert storage.get_model("v5_5_ru").warmup is True

    def test_yaml_without_warmup_defaults_to_false(self, tmp_path):
        """YAML without warmup field should default to False."""

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
    locales:
      ru_RU:
        voices:
          - name: aidar
            speaker: aidar
            model: v5_5_ru
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))

        assert storage.get_model("v5_5_ru").warmup is False


class TestYamlHashPrefixField:
    """Tests for parsing hash_prefix field from YAML config."""

    def test_yaml_hash_prefix_sets_hash_prefix_on_model(self, tmp_path):
        """YAML with hash_prefix should set hash_prefix on Model."""

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
          - name: aidar
            speaker: aidar
            model: v5_5_ru
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))

        assert storage.get_model("v5_5_ru").hash_prefix == "a1b2c3d4"

    def test_yaml_without_hash_prefix_defaults_to_none(self, tmp_path):
        """YAML without hash_prefix should default to None."""

        config_yml = tmp_path / "config.yml"
        config_yml.write_text(
            """
models:
  v5_5_ru:
    language: ru
    locales:
      ru_RU:
        voices:
          - name: aidar
            speaker: aidar
            model: v5_5_ru
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))

        assert storage.get_model("v5_5_ru").hash_prefix is None

    def test_yaml_empty_hash_prefix_defaults_to_none(self, tmp_path):
        """YAML with empty hash_prefix should default to None."""

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
          - name: aidar
            speaker: aidar
            model: v5_5_ru
"""
        )

        storage = SileroTTSYamlConfigStorage(str(config_yml))

        assert storage.get_model("v5_5_ru").hash_prefix is None


class TestDisabledModel:
    """Tests for model disabling via enabled=False on Model."""

    def test_disabled_model_voices_excluded_from_get_voices(self):
        """get_voices should exclude voices that reference a disabled model."""

        config_model = TTSConfigModel(
            models=[
                Model(name="v5_5_ru", language="ru", enabled=False),
                Model(name="v3_en", language="en", enabled=True),
            ],
            voices=[
                Voice(
                    id="ru_RU-v5_5_ru-aidar",
                    name="aidar",
                    speaker="aidar",
                    model="v5_5_ru",
                    locale="ru_RU",
                ),
                Voice(
                    id="en_US-v3_en-en_0",
                    name="en_0",
                    speaker="en_0",
                    model="v3_en",
                    locale="en_US",
                ),
            ],
        )

        storage = SileroTTSYamlConfigStorage(config_model)

        result = storage.get_voices()
        assert not any(v.locale == "ru_RU" for v in result)
        assert any(v.locale == "en_US" for v in result)
        assert any(v.name == "en_0" for v in result)

    def test_disabled_model_get_model_returns_none(self):
        """get_model should return None for a disabled model."""

        config_model = TTSConfigModel(
            models=[
                Model(name="v5_5_ru", language="ru", enabled=False),
            ],
            voices=[],
        )

        storage = SileroTTSYamlConfigStorage(config_model)

        assert storage.get_model("v5_5_ru") is None
