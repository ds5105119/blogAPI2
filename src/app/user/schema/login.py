from pydantic import BaseModel, EmailStr, Field, model_validator
from typing_extensions import Self


class LoginDto(BaseModel):
    email: EmailStr | None
    handle: str | None
    password: str = Field(min_length=8, max_length=30)

    @model_validator(mode="after")
    def check_email_or_handle(self) -> Self:
        if not (self.email or self.handle):
            raise ValueError("email and handle is empty.")
        return self


class LoginResponse(BaseModel):
    access: str
    refresh: str | None
