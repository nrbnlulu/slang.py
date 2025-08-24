from __future__ import annotations

from enum import Enum

from typing import Protocol



class Languages(Enum):
    """Available languages for translations."""

    EN = "en"




class Locale_en_nestedProto(Protocol):

    @property
    def content(self) -> str:
        raise NotImplementedError()

    @property
    def title(self) -> str:
        raise NotImplementedError()

    
class TranslationsProto(Protocol):
    def complex(self,name: str) -> str:
        raise NotImplementedError()

    
    @property
    def nested(self) -> Locale_en_nestedProto:
        raise NotImplementedError()

    @property
    def simple(self) -> str:
        raise NotImplementedError()


class Locale_en_nested(Locale_en_nestedProto):


    @property
    def content(self) -> str:
        return 'Nested Content'

    @property
    def title(self) -> str:
        return 'Nested Title'




class Translations_en(TranslationsProto):


    def complex(self, name: str) -> str:
        return 'Hello {name}!'.format(name=name)

    @property
    def nested(self) -> Locale_en_nestedProto:
        return Locale_en_nested()

    @property
    def simple(self) -> str:
        return 'Simple text'




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


    raise ValueError(f"Unsupported language: {language}")