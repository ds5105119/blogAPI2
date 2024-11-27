from argon2 import PasswordHasher
from pydantic import BaseModel, EmailStr, Field, field_serializer, field_validator, model_validator
from typing_extensions import Self

hasher = PasswordHasher()


class HandleDto(BaseModel):
    handle: str


class EmailDto(BaseModel):
    email: EmailStr


class RegisterDto(HandleDto, EmailDto):
    password1: str = Field(min_length=8, max_length=30, serialization_alias="password")
    password2: str = Field(min_length=8, max_length=30, exclude=True)

    @field_validator("password1")
    @classmethod
    def validate(cls, value: str):
        if value.isalpha():
            raise ValueError("password must contain numbers.")
        if value.isdigit():
            raise ValueError("password must contain letters.")
        return value

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        pw1 = self.password1
        pw2 = self.password2
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError("passwords do not match")
        return self

    @field_serializer("password1")
    def hash_password(self, password1: str) -> str:
        return hasher.hash(password1)
