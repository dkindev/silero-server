# Mary TTS core endpoints

## /locales (GET)

Returns a list of supported locales in the format [locale]\n..., for example “en_US” or “de_DE” or simply “en” etc.

## /voices (GET)

Returns a list of supported voices in the format [name] [locale] [gender]\n..., ‘name’ can be anything without spaces(!) and ‘gender’ is traditionally f (or female) or m (or male), for example "mu-slt-hsmm en_US female".

## /process (GET and POST)

Processes the input text and returns a wav file.

### Parameters

|Parameter|Description|Example|
|---|---|---|
|**`INPUT_TEXT`**|Text for voice-over|"Hello world"|
|**`INPUT_TYPE`**|Input data format|`TEXT`, `SSML`, `RAWMARYXML`|
|**`OUTPUT_TYPE`**|Output data format|`AUDIO` (по умолчанию), `PHONEMES`, `TOKENS`|
|**`LOCALE`**|Language code|`en_US`, `de_DE`, `ru_RU`|
|**`VOICE`**|Specific voice name|`cmu-slt-hsmm`, `bits1-hsmm`|
|**`AUDIO`**|Audio file format|`WAVE_FILE`, `AU_FILE`, `AIFF_FILE`|
