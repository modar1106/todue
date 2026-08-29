"""
Todo service — Business logic layer for Todo CRUD operations.
Handles Supabase queries with filtering, sorting, pagination, and bulk insert.
"""

import datetime
import math
import random
import time
from typing import Optional

import uuid6
from faker import Faker

from app.database import get_supabase_admin


fake = Faker()
_stats_cache: dict = {}


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

        query = (
            self.admin.table("todos")
            .select("*", count="exact")
            .eq("user_id", user_id)
        )

        if status:
            query = query.eq("status", status)

        if priority:
            query = query.eq("priority", priority)

        if due_date:
            query = query.eq("due_date", due_date)

        if project:
            if project.lower() == "inbox":
                query = query.or_("project.ilike.Inbox,project.is.null")
            else:
                query = query.ilike("project", project)

        if search:
            # Search in title and description using ilike (case-insensitive)
            search_pattern = f"%{search}%"
            query = query.or_(
                f"title.ilike.{search_pattern},description.ilike.{search_pattern}"
            )

        # Apply sorting
        is_descending = sort_order.lower() == "desc"
        query = query.order(sort_by, desc=is_descending)

        # Apply pagination (range is 0-indexed, inclusive)
        query = query.range(offset, offset + page_size - 1)

        try:
            result = query.execute()
            data = result.data
            total = result.count if result.count is not None else len(data)
        except Exception as err:
            err_str = str(err)
            if "PGRST204" in err_str or "schema cache" in err_str:
                # Graceful single-query fallback if project or due_date column is missing in Supabase
                fallback = (
                    self.admin.table("todos")
                    .select("*", count="exact")
                    .eq("user_id", user_id)
                )
                if status:
                    fallback = fallback.eq("status", status)
                if priority:
                    fallback = fallback.eq("priority", priority)
                if search:
                    sp = f"%{search}%"
                    fallback = fallback.or_(f"title.ilike.{sp},description.ilike.{sp}")

                result = fallback.order(sort_by, desc=is_descending).range(offset, offset + page_size - 1).execute()
                data = result.data
                total = result.count if result.count is not None else len(data)
            else:
                raise err

        total_pages = math.ceil(total / page_size) if page_size > 0 else 0

        return {
            "data": data,
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
        _stats_cache.pop(user_id, None)
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

        try:
            result = self.admin.table("todos").insert(todo_data).execute()
            return result.data[0]
        except Exception as err:
            err_str = str(err)
            if "PGRST204" in err_str or "schema cache" in err_str:
                # Fallback if due_date / project column has not been added to Supabase yet
                todo_data.pop("due_date", None)
                todo_data.pop("project", None)
                result = self.admin.table("todos").insert(todo_data).execute()
                return result.data[0]
            raise err

    def get_stats(self, user_id: str) -> dict:
        """
        Fetch task statistics count grouped by status for a user with in-memory caching.

        Args:
            user_id: Owner user ID

        Returns:
            dict with total (active tasks), pending, progress, done counts
        """
        now = time.time()
        if user_id in _stats_cache:
            entry = _stats_cache[user_id]
            if now - entry["timestamp"] < 10:  # 10s TTL
                return entry["data"]

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

        _stats_cache[user_id] = {"data": counts, "timestamp": now}
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
        _stats_cache.pop(user_id, None)
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return self.get_todo_by_id(todo_id, user_id)

        try:
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
        except Exception as err:
            err_str = str(err)
            if "PGRST204" in err_str or "schema cache" in err_str:
                update_data.pop("due_date", None)
                update_data.pop("project", None)
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
            raise err

    def delete_todo(self, todo_id: str, user_id: str) -> bool:
        """
        Delete a todo by ID in a single round-trip.

        Returns:
            True if deleted, False if not found/not owned.
        """
        _stats_cache.pop(user_id, None)
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
        _stats_cache.pop(user_id, None)
        statuses = ["pending", "progress", "done"]
        priorities = ["low", "medium", "high"]
        projects = ["Inbox", "Work", "Personal", "Study"]

        today = datetime.date.today()
        # Diverse sample due dates for upcoming/today views
        sample_due_dates = [
            (today + datetime.timedelta(days=d)).isoformat()
            for d in range(-2, 14)
        ] + [None, None]

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
                        "project": random.choice(projects),
                        "due_date": random.choice(sample_due_dates),
                    }
                )

            try:
                result = self.admin.table("todos").insert(batch).execute()
                total_inserted += len(result.data)
            except Exception as err:
                err_str = str(err)
                if "PGRST204" in err_str or "schema cache" in err_str:
                    for item in batch:
                        item.pop("due_date", None)
                        item.pop("project", None)
                    result = self.admin.table("todos").insert(batch).execute()
                    total_inserted += len(result.data)
                else:
                    raise err

        return total_inserted
