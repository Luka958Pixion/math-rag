from math_rag.infrastructure.services.arxiv import BaseArxivCategory


class EESSCategory(BaseArxivCategory):
    AS = 'audio_and_speech_processing'
    IV = 'image_and_video_processing'
    SP = 'signal_processing'
    SY = 'systems_and_control'
