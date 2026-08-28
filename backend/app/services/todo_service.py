"""
Todo service — Business logic layer for Todo CRUD operations.
Handles Supabase queries with filtering, sorting, pagination, and bulk insert.
"""

import math
import random
from typing import Optional

import uuid6
from faker import Faker

from app.database import get_supabase_admin


fake = Faker()


class TodoService:
    """Service class encapsulating all todo business logic."""

    # Valid sort fields (whitelist to prevent injection)
    VALID_SORT_FIELDS = {"title", "status", "priority", "created_at", "updated_at"}

    def __init__(self):
        self.admin = get_supabase_admin()

    def get_todos(
        self,
        user_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
        due_date: Optional[str] = None,
        project: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 10,
    ) -> dict:
        """
        Fetch paginated, filtered, and sorted todos for a user.

        Args:
            user_id: The authenticated user's ID
            status: Filter by status (pending/progress/done)
            priority: Filter by priority (low/medium/high)
            search: Search keyword for title/description (ilike)
            due_date: Filter by due_date (e.g. YYYY-MM-DD)
            project: Filter by project name
            sort_by: Field to sort by
            sort_order: Sort direction (asc/desc)
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            dict with data, total, page, page_size, total_pages
        """
        # Validate sort field against whitelist
        if sort_by not in self.VALID_SORT_FIELDS:
            sort_by = "created_at"

        # Calculate offset
        offset = (page - 1) * page_size

        # --- Count query (for total) ---
        count_query = (
            self.admin.table("todos")
            .select("id", count="exact")
            .eq("user_id", user_id)
        )

        # --- Data query ---
        data_query = (
            self.admin.table("todos")
            .select("*")
            .eq("user_id", user_id)
        )

        # Apply filters to both queries
        if status:
            count_query = count_query.eq("status", status)
            data_query = data_query.eq("status", status)

        if priority:
            count_query = count_query.eq("priority", priority)
            data_query = data_query.eq("priority", priority)

        if due_date:
            count_query = count_query.eq("due_date", due_date)
            data_query = data_query.eq("due_date", due_date)

        if project:
            count_query = count_query.eq("project", project)
            data_query = data_query.eq("project", project)

        if search:
            # Search in title and description using ilike (case-insensitive)
            search_pattern = f"%{search}%"
            count_query = count_query.or_(
                f"title.ilike.{search_pattern},description.ilike.{search_pattern}"
            )
            data_query = data_query.or_(
                f"title.ilike.{search_pattern},description.ilike.{search_pattern}"
            )

        # Execute count query
        count_result = count_query.execute()
        total = count_result.count if count_result.count is not None else 0

        # Apply sorting
        is_descending = sort_order.lower() == "desc"
        data_query = data_query.order(sort_by, desc=is_descending)

        # Apply pagination (range is 0-indexed, inclusive)
        data_query = data_query.range(offset, offset + page_size - 1)

        # Execute data query
        data_result = data_query.execute()

        total_pages = math.ceil(total / page_size) if page_size > 0 else 0

        return {
            "data": data_result.data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    def get_todo_by_id(self, todo_id: str, user_id: str) -> Optional[dict]:
        """
        Fetch a single todo by ID, ensuring it belongs to the user.

        Returns:
            Todo dict or None if not found/not owned.
        """
        result = (
            self.admin.table("todos")
            .select("*")
            .eq("id", todo_id)
            .eq("user_id", user_id)
            .execute()
        )
        if result.data:
            return result.data[0]
        return None

    def create_todo(self, user_id: str, data: dict) -> dict:
        """
        Create a single todo with UUIDv7.

        Args:
            user_id: Owner user ID
            data: Todo fields (title, description, status, priority, due_date, project)

        Returns:
            Created todo dict
        """
        todo_data = {
            "id": str(uuid6.uuid7()),
            "user_id": user_id,
            "title": data["title"],
            "description": data.get("description", ""),
            "status": data.get("status", "pending"),
            "priority": data.get("priority", "low"),
            "due_date": data.get("due_date", None),
            "project": data.get("project", "Inbox"),
        }

        result = self.admin.table("todos").insert(todo_data).execute()
        return result.data[0]

    def get_stats(self, user_id: str) -> dict:
        """
        Fetch task statistics count grouped by status for a user in a single query.

        Args:
            user_id: Owner user ID

        Returns:
            dict with total (active tasks), pending, progress, done counts
        """
        result = (
            self.admin.table("todos")
            .select("status")
            .eq("user_id", user_id)
            .execute()
        )

        counts = {"total": 0, "pending": 0, "progress": 0, "done": 0}
        if result.data:
            for row in result.data:
                st = row.get("status")
                if st in counts:
                    counts[st] += 1
            # Total active/uncompleted tasks for badges
            counts["total"] = counts["pending"] + counts["progress"]

        return counts

    def update_todo(self, todo_id: str, user_id: str, data: dict) -> Optional[dict]:
        """
        Update an existing todo in a single database round-trip.

        Args:
            todo_id: Todo UUID to update
            user_id: Owner user ID (for isolation check)
            data: Fields to update

        Returns:
            Updated todo dict or None if not found/not owned.
        """
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return self.get_todo_by_id(todo_id, user_id)

        result = (
            self.admin.table("todos")
            .update(update_data)
            .eq("id", todo_id)
            .eq("user_id", user_id)
            .execute()
        )

        if result.data and len(result.data) > 0:
            return result.data[0]
        return None

    def delete_todo(self, todo_id: str, user_id: str) -> bool:
        """
        Delete a todo by ID in a single round-trip.

        Returns:
            True if deleted, False if not found/not owned.
        """
        result = (
            self.admin.table("todos")
            .delete()
            .eq("id", todo_id)
            .eq("user_id", user_id)
            .execute()
        )
        return bool(result.data and len(result.data) > 0)

    def generate_bulk_todos(self, user_id: str, count: int = 1000) -> int:
        """
        Generate random todos using Faker library with UUIDv7 IDs.
        Inserts in batches of 100 for performance.

        Args:
            user_id: Owner user ID
            count: Number of todos to generate (default 1000)

        Returns:
            Number of todos successfully created.
        """
        statuses = ["pending", "progress", "done"]
        priorities = ["low", "medium", "high"]

        # Task title templates for variety
        task_templates = [
            lambda: f"Review {fake.catch_phrase()}",
            lambda: f"Complete {fake.bs()}",
            lambda: f"Prepare {fake.word().capitalize()} report",
            lambda: f"Meeting with {fake.name()}",
            lambda: f"Fix bug in {fake.file_name(extension='py')}",
            lambda: f"Deploy {fake.domain_word()} service",
            lambda: f"Update {fake.word()} documentation",
            lambda: f"Refactor {fake.word()} module",
            lambda: f"Design {fake.word()} feature",
            lambda: f"Test {fake.word()} integration",
            lambda: fake.sentence(nb_words=random.randint(3, 8)).rstrip("."),
        ]

        total_inserted = 0
        batch_size = 100

        for i in range(0, count, batch_size):
            batch = []
            current_batch_size = min(batch_size, count - i)

            for _ in range(current_batch_size):
                template = random.choice(task_templates)
                batch.append(
                    {
                        "id": str(uuid6.uuid7()),
                        "user_id": user_id,
                        "title": template(),
                        "description": fake.paragraph(nb_sentences=random.randint(1, 4)),
                        "status": random.choice(statuses),
                        "priority": random.choice(priorities),
                    }
                )

            result = self.admin.table("todos").insert(batch).execute()
            total_inserted += len(result.data)

        return total_inserted
