"""
Todo CRUD routes — Protected by JWT authentication.
All operations are scoped to the authenticated user's todos.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.models import (
    BulkGenerateResponse,
    ErrorResponse,
    SuccessResponse,
    TodoCreate,
    TodoListResponse,
    TodoPriority,
    TodoResponse,
    TodoSortField,
    TodoStatsResponse,
    TodoStatus,
    TodoUpdate,
    SortOrder,
)
from app.security import CurrentUser, get_current_user
from app.services.todo_service import TodoService

router = APIRouter(prefix="/api/todos", tags=["Todos"])


def get_todo_service() -> TodoService:
    """Dependency to get TodoService instance."""
    return TodoService()


# ============================================================
# GET /api/todos/stats — Get todo stats count
# ============================================================

@router.get(
    "/stats",
    response_model=TodoStatsResponse,
    summary="Get todo statistics count for the current user",
)
async def get_todo_stats(
    current_user: CurrentUser = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """Fetch task statistics counts (total, pending, in progress, done)."""
    stats = service.get_stats(user_id=current_user.id)
    return TodoStatsResponse(**stats)


# ============================================================
# GET /api/todos — List with filtering, sorting, pagination
# ============================================================

@router.get(
    "",
    response_model=TodoListResponse,
    summary="List todos with filtering, sorting, and pagination",
)
async def list_todos(
    status: TodoStatus | None = Query(None, description="Filter by status"),
    priority: TodoPriority | None = Query(None, description="Filter by priority"),
    search: str | None = Query(None, max_length=200, description="Search in title/description"),
    due_date: str | None = Query(None, description="Filter by due_date (YYYY-MM-DD)"),
    project: str | None = Query(None, description="Filter by project"),
    sort_by: TodoSortField = Query(TodoSortField.CREATED_AT, description="Sort field"),
    sort_order: SortOrder = Query(SortOrder.DESC, description="Sort direction"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    current_user: CurrentUser = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """
    Fetch the authenticated user's todos with optional filtering, sorting, and pagination.
    """
    result = service.get_todos(
        user_id=current_user.id,
        status=status.value if status else None,
        priority=priority.value if priority else None,
        search=search,
        due_date=due_date,
        project=project,
        sort_by=sort_by.value,
        sort_order=sort_order.value,
        page=page,
        page_size=page_size,
    )

    return TodoListResponse(
        data=[TodoResponse(**item) for item in result["data"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        total_pages=result["total_pages"],
    )


# ============================================================
# GET /api/todos/{id} — Get single todo
# ============================================================

@router.get(
    "/{todo_id}",
    response_model=TodoResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get a single todo by ID",
)
async def get_todo(
    todo_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """Fetch a single todo. Returns 404 if not found or not owned by the user."""
    todo = service.get_todo_by_id(todo_id, current_user.id)

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found or access denied.",
        )

    return TodoResponse(**todo)


# ============================================================
# POST /api/todos — Create single todo
# ============================================================

@router.post(
    "",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new todo",
)
async def create_todo(
    body: TodoCreate,
    current_user: CurrentUser = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """
    Create a new todo with a UUIDv7 identifier.
    The todo is automatically associated with the authenticated user.
    """
    try:
        todo = service.create_todo(
            user_id=current_user.id,
            data=body.model_dump(),
        )
        return TodoResponse(**todo)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task in database: {str(e)}",
        )


# ============================================================
# PUT /api/todos/{id} — Update todo
# ============================================================

@router.put(
    "/{todo_id}",
    response_model=TodoResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Update an existing todo",
)
async def update_todo(
    todo_id: str,
    body: TodoUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """
    Update a todo's fields. Only provided (non-null) fields are updated.
    Returns 404 if not found or not owned by the user.
    """
    updated = service.update_todo(
        todo_id=todo_id,
        user_id=current_user.id,
        data=body.model_dump(exclude_none=True),
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found or access denied.",
        )

    return TodoResponse(**updated)


# ============================================================
# DELETE /api/todos/{id} — Delete todo
# ============================================================

@router.delete(
    "/{todo_id}",
    response_model=SuccessResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Delete a todo",
)
async def delete_todo(
    todo_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """Delete a todo. Returns 404 if not found or not owned by the user."""
    deleted = service.delete_todo(todo_id, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found or access denied.",
        )

    return SuccessResponse(message="Todo deleted successfully.")


# ============================================================
# POST /api/todos/generate-bulk — Generate 1000 random todos
# ============================================================

@router.post(
    "/generate-bulk",
    response_model=BulkGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate 1,000 random sample todos",
)
async def generate_bulk_todos(
    count: int = Query(1000, ge=1, le=5000, description="Number of todos to generate"),
    current_user: CurrentUser = Depends(get_current_user),
    service: TodoService = Depends(get_todo_service),
):
    """
    Generate random sample todos using Faker library.
    Each todo gets a UUIDv7 ID and belongs to the authenticated user.
    Inserted in batches of 100 for optimal performance.
    """
    total_created = service.generate_bulk_todos(
        user_id=current_user.id,
        count=count,
    )

    return BulkGenerateResponse(
        message=f"Successfully generated {total_created} random todos.",
        count=total_created,
    )
