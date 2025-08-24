from __future__ import annotations

from enum import Enum

from typing import Protocol



class Languages(Enum):
    """Available languages for translations."""

    EN = "en"

    FR = "fr"




class TranslationsProto(Protocol):
    @property
    def au_revoir(self) -> str:
        raise NotImplementedError()

    @property
    def bonjour(self) -> str:
        raise NotImplementedError()


class Translations_en(TranslationsProto):


    @property
    def au_revoir(self) -> str:
        return 'Goodbye'

    @property
    def bonjour(self) -> str:
        return 'Hello'




class Translations_fr(TranslationsProto):


    @property
    def au_revoir(self) -> str:
        return 'Au revoir'

    @property
    def bonjour(self) -> str:
        return 'Bonjour'




def get_translations(language: Languages) -> TranslationsProto:
    """Get translations for the specified language.

    Args:
        language: The language to get translations for

    Returns:
        Translations instance for the specified language
    """
    match language:

        case Languages.EN:
            return Translations_en()

        case Languages.FR:
            return Translations_fr()


    raise ValueError(f"Unsupported language: {language}")