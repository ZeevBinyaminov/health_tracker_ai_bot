from typing import Any

from sqlalchemy.types import JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base(
    type_annotation_map={
        dict[str, Any]: JSON
    }
)
