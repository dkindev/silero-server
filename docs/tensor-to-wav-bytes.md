# Hot to convert PyTorch tensor to WAV bytes for Silero models

## Configuration on CPU ONLY

```python
import io
import numpy as np
import scipy.io.wavfile as wavfile

# audio is already on the CPU, form: [1, samples] or [samples]
audio_np = audio.squeeze().detach().numpy()

# Clipping protection: hard limit values ​​in the range [-1.0, 1.0]
audio_np = np.clip(audio_np, -1.0, 1.0)

# Safe conversion to 16-bit PCM
pcm_data = (audio_np * 32767).astype(np.int16)

buffer = io.BytesIO()
wavfile.write(buffer, sample_rate, pcm_data)
buffer.seek(0)
```

## Configuration ONLY on GPU (No transfer to CPU) if device = cuda

```python
import io
import torch
import torchcodec

# audio is on the GPU (cuda), format: [channels, samples]
# For WAV (PCM 16-bit), conversion to int16 on the GPU is instantaneous
audio_gpu = torch.clamp(audio, -1.0, 1.0)
pcm_gpu = (audio_gpu * 32767).to(torch.int16)

# Native memory encoding with torchcodec WITHOUT switching to CPU
# Note: Make sure the channel and sample axis are set correctly for your model.
audio_bytes = torchcodec.encoders.encode_audio(
    pcm_gpu, 
    sample_rate=sample_rate, 
    format="wav"
)

# If the calling code strictly requires an io.BytesIO object:
buffer = io.BytesIO(audio_bytes)

```

## Configuration ONLY on GPU (No transfer to CPU) if device = xpu
```python
import io
import torch
# Mandatory PyTorch extension for Intel graphics
import intel_extension_for_pytorch as ipex 
import torchcodec
# Importing the XPU plugin for hardware acceleration of Intel codecs
import torchcodec_xpu 

# Let's assume the audio is on an xpu device
device = torch.device("xpu:0")
audio_xpu = audio.to(device) # Формат: [channels, samples]

# 1. Safe amplitude limiting (clipping) on ​​XPU
audio_xpu = torch.clamp(audio_xpu, -1.0, 1.0)

# 2. Instant conversion to 16-bit PCM on the XPU side
pcm_xpu = (audio_xpu * 32767).to(torch.int16)

# 3. Audio encoding with explicit XPU backend
audio_bytes = torchcodec.encoders.encode_audio(
    pcm_xpu, 
    sample_rate=sample_rate, 
    format="wav"
)

# Wrapping into a byte buffer
buffer = io.BytesIO(audio_bytes)
buffer.seek(0)
```

## Fast Hybrid Method: CPU Porting (SciPy on CPU)
```python
import io
import numpy as np
import scipy.io.wavfile as wavfile

# audio is located on device 'xpu/cuda'
# We transfer it to the CPU and convert it into a numpy array.
audio_np = audio.squeeze().clamp(-1.0, 1.0).cpu().numpy()

# Scaling to 16-bit PCM
pcm_data = (audio_np * 32767).astype(np.int16)

# Writing to an in-memory buffer using SciPy
buffer = io.BytesIO()
wavfile.write(buffer, sample_rate, pcm_data)
buffer.seek(0)
```