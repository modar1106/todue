"""
Supabase client initialization module.
Provides two clients:
  - supabase_client: Uses anon key (respects RLS, for user-scoped queries)
  - supabase_admin: Uses service_role key (bypasses RLS, for admin/bulk operations)
"""

from supabase import create_client, Client
from app.config import get_settings


def get_supabase_client() -> Client:
    """
    Get Supabase client with anon key.
    This client respects Row Level Security policies.
    """
    settings = get_settings()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


def get_supabase_admin() -> Client:
    """
    Get Supabase client with service_role key.
    This client BYPASSES Row Level Security — use only for
    trusted server-side operations like bulk insert.
    """
    settings = get_settings()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
