from typing import Literal

from pydantic import Field, model_validator

from app.contracts import StrictModel
from app.domain.rules import RuleSpec


class RuleRequest(StrictModel):
    name: str = Field(min_length=1, max_length=60)
    field: Literal["presence", "occupancy"]
    threshold: int = Field(ge=0, le=20, strict=True)

    @model_validator(mode="after")
    def coherent(self):
        RuleSpec(self.name, self.field, self.threshold)
        return self
