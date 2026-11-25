from typing import Annotated

from pydantic import BaseModel, ConfigDict, FiniteFloat, StringConstraints


class CreateHeatLookup(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    profile: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    thick: FiniteFloat
    target: FiniteFloat
    measured: FiniteFloat


class ConfirmHeatLookup(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
