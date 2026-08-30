"""
Todo service — Business logic layer for Todo CRUD operations.
Split into focused methods per view for clarity and maintainability.
"""

import datetime
import math
import random
import time
import threading
import logging
from typing import Optional

import uuid6
from faker import Faker

from app.database import get_supabase_admin

logger = logging.getLogger(__name__)
fake = Faker()

# Thread-safe stats cache
_stats_cache: dict = {}
_stats_lock = threading.Lock()

# Module-level singleton
_service_instance: Optional["TodoService"] = None
_service_lock = threading.Lock()


def get_todo_service() -> "TodoService":
    """Get or create the singleton TodoService instance."""
    global _service_instance
    if _service_instance is None:
        with _service_lock:
            if _service_instance is None:
                _service_instance = TodoService()
    return _service_instance


class TodoService:
    """Service class encapsulating all todo business logic."""

    # Valid sort fields (whitelist to prevent injection)
    VALID_SORT_FIELDS = {"title", "status", "priority", "due_date", "created_at", "updated_at"}

    def __init__(self):
        self.admin = get_supabase_admin()

    # ================================================================
    # STATS — Single PostgreSQL RPC (~5ms) with thread-safe cache
    # ================================================================

    def get_stats(self, user_id: str) -> dict:
        """
        Fetch task statistics count grouped by status for a user.
        Uses PostgreSQL RPC function for instant counting (no 1000-row limit).
        Falls back to parallel count queries if RPC is not available.

        Returns:
            dict with total, active, pending, progress, done counts
        """
        now = time.time()
        with _stats_lock:
            if user_id in _stats_cache:
                entry = _stats_cache[user_id]
                if now - entry["timestamp"] < 60:  # 60s TTL, invalidated on mutate
                    return entry["data"]

        # Strategy 1: PostgreSQL RPC (fastest, ~5ms)
        try:
            result = self.admin.rpc(
                "get_user_todo_stats", {"p_user_id": user_id}
            ).execute()
            if result.data:
                counts = result.data if isinstance(result.data, dict) else result.data[0] if isinstance(result.data, list) else {}
                # Ensure all expected keys exist
                counts.setdefault("total", 0)
                counts.setdefault("active", 0)
                counts.setdefault("pending", 0)
                counts.setdefault("progress", 0)
                counts.setdefault("done", 0)

                with _stats_lock:
                    _stats_cache[user_id] = {"data": counts, "timestamp": time.time()}
                return counts
        except Exception as e:
            logger.debug("RPC get_user_todo_stats not available, using fallback: %s", e)

        # Strategy 2: Fallback — count queries with limit(0) to bypass PostgREST 1000-row cap
        try:
            counts = {"total": 0, "active": 0, "pending": 0, "progress": 0, "done": 0}

            r_pending = (
                self.admin.table("todos")
                .select("id", count="exact")
                .eq("user_id", user_id)
                .eq("status", "pending")
                .limit(0)
                .execute()
            )
            r_progress = (
                self.admin.table("todos")
                .select("id", count="exact")
                .eq("user_id", user_id)
                .eq("status", "progress")
                .limit(0)
                .execute()
            )
            r_done = (
                self.admin.table("todos")
                .select("id", count="exact")
                .eq("user_id", user_id)
                .eq("status", "done")
                .limit(0)
                .execute()
            )

            counts["pending"] = r_pending.count or 0
            counts["progress"] = r_progress.count or 0
            counts["done"] = r_done.count or 0
            counts["active"] = counts["pending"] + counts["progress"]
            counts["total"] = counts["active"] + counts["done"]

            with _stats_lock:
                _stats_cache[user_id] = {"data": counts, "timestamp": time.time()}
            return counts

        except Exception as e:
            logger.error("Failed to fetch stats for user %s: %s", user_id, e)
            return {"total": 0, "active": 0, "pending": 0, "progress": 0, "done": 0}

    def _invalidate_stats(self, user_id: str):
        """Invalidate the stats cache for a user after mutations."""
        with _stats_lock:
            _stats_cache.pop(user_id, None)

    # ================================================================
    # INBOX — Paginated listing of active todos (general purpose)
    # Handles: Inbox view, Project filter, Priority filter, Search
    # ================================================================

    def get_inbox_todos(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        status: Optional[str] = None,
        priority: Optional[str] = None,
        project: Optional[str] = None,
        search: Optional[str] = None,
    ) -> dict:
        """
        Fetch paginated todos for Inbox/Project/Search views with optional status filter.

        Returns:
            dict with data, total, page, page_size, total_pages
        """
        if sort_by not in self.VALID_SORT_FIELDS:
            sort_by = "created_at"

        offset = (page - 1) * page_size

        # Use exact count when search/project/priority/status filters are active
        has_filters = bool(search or priority or status or (project and project.lower() != "inbox"))
        if has_filters:
            query = self.admin.table("todos").select("*", count="exact").eq("user_id", user_id)
        else:
            query = self.admin.table("todos").select("*").eq("user_id", user_id)

        # Apply status filtering
        if status:
            if status == "done":
                query = query.eq("status", "done")
            elif status == "pending":
                query = query.eq("status", "pending")
            elif status == "progress":
                query = query.eq("status", "progress")
            elif status == "active":
                query = query.neq("status", "done")
            # 'all' does not add any status filter
        else:
            # Default Inbox shows active tasks (not done)
            query = query.neq("status", "done")

        if priority:
            query = query.eq("priority", priority)

        if project:
            if project.lower() == "inbox":
                query = query.or_("project.ilike.Inbox,project.is.null")
            else:
                query = query.ilike("project", project)

        if search:
            search_pattern = f"%{search}%"
            query = query.or_(
                f"title.ilike.{search_pattern},description.ilike.{search_pattern}"
            )

        # Apply sorting
        is_descending = sort_order.lower() == "desc"
        if sort_by == "due_date":
            query = query.order(sort_by, desc=is_descending, nullsfirst=False)
        else:
            query = query.order(sort_by, desc=is_descending)

        # Apply pagination
        query = query.range(offset, offset + page_size - 1)

        result = query.execute()
        data = result.data

        # Determine total count
        if has_filters and result.count is not None:
            total = result.count
        elif page == 1 and len(data) < page_size:
            total = len(data)
        else:
            stats = self.get_stats(user_id)
            total = stats.get("active", 0)

        total = max(total, offset + len(data))
        total_pages = math.ceil(total / page_size) if page_size > 0 else 0

        return {
            "data": data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    # ================================================================
    # TODAY — Tasks due today or overdue
    # ================================================================

    def get_today_todos(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 10,
    ) -> dict:
        """
        Fetch tasks due today or overdue (past due_date, not done).
        Sorted by due_date ascending (most urgent first).

        Returns:
            dict with data, total, page, page_size, total_pages
        """
        today_str = datetime.date.today().isoformat()
        offset = (page - 1) * page_size

        query = (
            self.admin.table("todos")
            .select("*", count="exact")
            .eq("user_id", user_id)
            .neq("status", "done")
            .lte("due_date", today_str)
            .order("due_date", desc=False, nullsfirst=False)
            .range(offset, offset + page_size - 1)
        )

        result = query.execute()
        data = result.data
        total = result.count if result.count is not None else len(data)
        total = max(total, offset + len(data))
        total_pages = math.ceil(total / page_size) if page_size > 0 else 0

        return {
            "data": data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    # ================================================================
    # UPCOMING — Tasks in a date range (no pagination)
    # ================================================================

    def get_upcoming_todos(
        self,
        user_id: str,
        start_date: str,
        end_date: str,
    ) -> list:
        """
        Fetch all active tasks within a date range for the upcoming/calendar view.
        No pagination — a typical week has 5-30 tasks.
        Sorted by due_date ascending.

        Args:
            user_id: Owner user ID
            start_date: Start of range (YYYY-MM-DD, inclusive)
            end_date: End of range (YYYY-MM-DD, inclusive)

        Returns:
            list of todo dicts
        """
        result = (
            self.admin.table("todos")
            .select("*")
            .eq("user_id", user_id)
            .neq("status", "done")
            .gte("due_date", start_date)
            .lte("due_date", end_date)
            .order("due_date", desc=False, nullsfirst=False)
            .execute()
        )
        return result.data

    # ================================================================
    # COMPLETED — Done tasks (paginated)
    # ================================================================

    def get_completed_todos(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 10,
    ) -> dict:
        """
        Fetch paginated completed tasks.
        Sorted by updated_at descending (most recently completed first).

        Returns:
            dict with data, total, page, page_size, total_pages
        """
        offset = (page - 1) * page_size

        query = (
            self.admin.table("todos")
            .select("*")
            .eq("user_id", user_id)
            .eq("status", "done")
            .order("updated_at", desc=True)
            .range(offset, offset + page_size - 1)
        )

        result = query.execute()
        data = result.data

        # Use cached stats for total (faster than count="exact")
        if page == 1 and len(data) < page_size:
            total = len(data)
        else:
            stats = self.get_stats(user_id)
            total = stats.get("done", 0)

        total = max(total, offset + len(data))
        total_pages = math.ceil(total / page_size) if page_size > 0 else 0

        return {
            "data": data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    # ================================================================
    # SINGLE TODO — Get by ID
    # ================================================================

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

    # ================================================================
    # CREATE
    # ================================================================

    def create_todo(self, user_id: str, data: dict) -> dict:
        """
        Create a single todo with UUIDv7.

        Args:
            user_id: Owner user ID
            data: Todo fields (title, description, status, priority, due_date, project)

        Returns:
            Created todo dict
        """
        self._invalidate_stats(user_id)
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

    # ================================================================
    # UPDATE
    # ================================================================

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
        self._invalidate_stats(user_id)
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

    # ================================================================
    # DELETE
    # ================================================================

    def delete_todo(self, todo_id: str, user_id: str) -> bool:
        """
        Delete a todo by ID in a single round-trip.

        Returns:
            True if deleted, False if not found/not owned.
        """
        self._invalidate_stats(user_id)
        result = (
            self.admin.table("todos")
            .delete()
            .eq("id", todo_id)
            .eq("user_id", user_id)
            .execute()
        )
        return bool(result.data and len(result.data) > 0)

    # ================================================================
    # BULK GENERATE — Test data
    # ================================================================

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
        self._invalidate_stats(user_id)
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

            result = self.admin.table("todos").insert(batch).execute()
            total_inserted += len(result.data)

        return total_inserted
