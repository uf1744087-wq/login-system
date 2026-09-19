from pydantic import BaseModel,Field, ConfigDict
from typing import Annotated

class UserRequest(BaseModel):
    username: Annotated[str, Field(min_length=2, max_length=50)]
    full_name: Annotated[str, Field(min_length=2, max_length=255)]


class UserCreate(UserRequest):
    password: Annotated[str, Field(min_length=10, max_length=50)]


class UserResponse(UserRequest):
    model_config = ConfigDict(from_attributes=True)

    id: int


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class SignupResponse(BaseModel):
    message: str
    user: UserResponse