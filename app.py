import torch
import torchaudio

language = 'ru'
model_id = 'v5_5_ru'
sample_rate = 48000
device = torch.device('cpu')

model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                          model='silero_tts',
                          language=language,
                          speaker=model_id)
model.to(device)  # gpu or cpu

example_text = """
    Спасибо Бабушка Валя!
"""

speakers = ["aidar", "baya", "eugene", "kseniya", "xenia"]
for speaker in speakers:
    audio = model.apply_tts(text=example_text,
                            speaker=speaker,
                            sample_rate=sample_rate)

    torchaudio.save(f'.dist/output-{speaker}-{model_id}.wav', audio, sample_rate)
