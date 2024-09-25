from dataclasses import dataclass

from toolbox.infra.base_object import BaseObject


@dataclass
class TraceLayer(BaseObject):
    """
    Identifies a layer being traced.
    """
    parent: str
    child: str
