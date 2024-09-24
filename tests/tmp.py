
from __future__ import annotations
from typing import Protocol

class Locale_heb_namespaceProto(Protocol):

    @property
    def simple(self) -> str:
        raise NotImplementedError()

    def complex(self,arg1: str) -> str:
        raise NotImplementedError()

    
class TranslationsProto(Protocol):
    
    @property
    def namespace(self) -> Locale_heb_namespaceProto:
        raise NotImplementedError()

    
