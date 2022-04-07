from pydantic import BaseModel


class SuccessfulResponse(BaseModel):
    status_code: int = 200
    content: str


class CreatedResponse(BaseModel):
    status_code: int = 201
    content: str


class BadRequest(BaseModel):
    status_code: int = 400
    content: str


class Unauthorized(BaseModel):
    status_code: int = 401
    content: str


class NotFound(BaseModel):
    status_code: int = 404
    content: str
