
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ============================================================
# Enums
# ============================================================

class TodoStatus(str, Enum):
    """Todo item status values."""
    PENDING = "pending"
    PROGRESS = "progress"
    DONE = "done"


class TodoPriority(str, Enum):
    """Todo item priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SortOrder(str, Enum):
    """Sort direction."""
    ASC = "asc"
    DESC = "desc"


class TodoSortField(str, Enum):
    """Allowed fields for sorting todos."""
    TITLE = "title"
    STATUS = "status"
    PRIORITY = "priority"
    DUE_DATE = "due_date"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


# ============================================================
# Auth Schemas
# ============================================================

class AuthRegisterRequest(BaseModel):
    """Registration request body."""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    full_name: Optional[str] = Field(None, max_length=255)


class AuthLoginRequest(BaseModel):
    """Login request body."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class AuthResponse(BaseModel):
    """Authentication response with tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserProfile"


class UserProfile(BaseModel):
    """User profile data."""
    id: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str = "user"
    created_at: Optional[str] = None


# ============================================================
# Todo Schemas
# ============================================================

class TodoCreate(BaseModel):
    """Request body for creating a new todo."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field("", max_length=5000)
    status: TodoStatus = TodoStatus.PENDING
    priority: TodoPriority = TodoPriority.LOW
    due_date: Optional[str] = None
    project: Optional[str] = "Inbox"


class TodoUpdate(BaseModel):
    """Request body for updating an existing todo. All fields optional."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[TodoStatus] = None
    priority: Optional[TodoPriority] = None
    due_date: Optional[str] = None
    project: Optional[str] = None


class TodoResponse(BaseModel):
    """Single todo item response."""
    id: str
    user_id: str
    title: str
    description: Optional[str] = ""
    status: str
    priority: str
    due_date: Optional[str] = None
    project: Optional[str] = "Inbox"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class TodoListResponse(BaseModel):
    """Paginated list of todos with metadata."""
    data: list[TodoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class TodoUpcomingResponse(BaseModel):
    """Upcoming view response — all tasks in a date range, no pagination."""
    data: list[TodoResponse]
    start_date: str
    end_date: str
    total: int


class TodoStatsResponse(BaseModel):
    """Statistics count response."""
    total: int = 0
    active: int = 0
    pending: int = 0
    progress: int = 0
    done: int = 0


class BulkGenerateResponse(BaseModel):
    """Response for bulk todo generation."""
    message: str
    count: int


# ============================================================
# API Response Wrappers
# ============================================================

class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool = True
    message: str


class ErrorResponse(BaseModel):
    """Generic error response."""
    success: bool = False
    error: str
    detail: Optional[str] = None
