"""
File: app/schemas/common.py
Purpose: Shared Pydantic response envelope schemas used across all API endpoints.
Responsibilities:
  - Wrap all API responses in a consistent {success, data, message} structure
  - Provide a generic paginated response type
  - Provide a structured error response schema
Dependencies:
  - pydantic
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """
    Description: Standard success response wrapper for all API endpoints.
    Responsibilities:
      - Ensure every response has a consistent shape
      - Carry typed data payload
    """

    success: bool = True
    data: T
    message: str | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Description: Paginated list response for collection endpoints.
    Responsibilities:
      - Wrap list results with pagination metadata
    """

    items: list[T]
    total: int
    page: int
    page_size: int


class ErrorDetail(BaseModel):
    """
    Description: Structured error payload inside an error response.
    """

    code: str
    message: str
    details: dict = {}


class ErrorResponse(BaseModel):
    """
    Description: Standard error response wrapper.
    """

    success: bool = False
    error: ErrorDetail
