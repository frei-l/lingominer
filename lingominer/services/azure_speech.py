import asyncio
import os

import azure.cognitiveservices.speech as speechsdk

from lingominer.logger import logger


async def generate_audio(text: str, filename: str, voice_code: str):
    speech_config = speechsdk.SpeechConfig(
        subscription=os.environ.get("AZURE_SPEECH_KEY"),
        region=os.environ.get("AZURE_SPEECH_REGION"),
    )
    speech_config.speech_synthesis_voice_name = voice_code
    audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config
    )
    speech_synthesis_result = await asyncio.to_thread(
        speech_synthesizer.speak_text_async(text).get
    )

    if (
        speech_synthesis_result.reason
        == speechsdk.ResultReason.SynthesizingAudioCompleted
    ):
        logger.info(f"Speech synthesized for text [{text}]")
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        logger.error(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                logger.error(f"Error details: {cancellation_details.error_details}")
                logger.error("Did you set the speech resource key and region values?")

