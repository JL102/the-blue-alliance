from typing import Any, Optional

class Key:
    def __init__(self, *path_args: Any, **kwargs: Any) -> None: ...
    def __eq__(self, other: Any) -> Any: ...
    def __ne__(self, other: Any) -> Any: ...
    def __hash__(self) -> Any: ...
    def completed_key(self, id_or_name: Any): ...
    def to_protobuf(self): ...
    def to_legacy_urlsafe(self, location_prefix: Optional[Any] = ...): ...
    @classmethod
    def from_legacy_urlsafe(cls, urlsafe: Any): ...
    @property
    def is_partial(self): ...
    @property
    def namespace(self): ...
    @property
    def path(self): ...
    @property
    def flat_path(self): ...
    @property
    def kind(self): ...
    @property
    def id(self): ...
    @property
    def name(self): ...
    @property
    def id_or_name(self): ...
    @property
    def project(self): ...
    @property
    def parent(self): ...