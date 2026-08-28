-- ============================================================
-- Todue  Clone — Supabase Database Migration
-- Run this script in the Supabase SQL Editor
-- ============================================================

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. PUBLIC USERS / PROFILES TABLE
--    Linked to Supabase Auth (auth.users)
-- ============================================================

CREATE TABLE IF NOT EXISTS public.users (
    id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email       VARCHAR(255) NOT NULL UNIQUE,
    full_name   VARCHAR(255),
    avatar_url  TEXT,
    role        VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.users IS 'Public profile table mirroring Supabase Auth users';
COMMENT ON COLUMN public.users.role IS 'Role field for future admin dashboard extensibility';

-- Trigger: Auto-create profile when a new user signs up via Supabase Auth
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, full_name, avatar_url)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1)),
        NEW.raw_user_meta_data->>'avatar_url'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop existing trigger if any, then create
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================================
-- 2. TODOS TABLE (with user_id foreign key)
-- ============================================================

CREATE TABLE IF NOT EXISTS public.todos (
    id          UUID PRIMARY KEY,               -- Generated as UUIDv7 in Python backend
    user_id     UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    title       VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    status      VARCHAR(20) DEFAULT 'pending'
                    CHECK (status IN ('pending', 'progress', 'done')),
    priority    VARCHAR(10) DEFAULT 'low'
                    CHECK (priority IN ('low', 'medium', 'high')),
    due_date    VARCHAR(50) DEFAULT NULL,
    project     VARCHAR(100) DEFAULT 'Inbox',
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.todos IS 'User todo items with status and priority tracking';

-- Trigger: Auto-update updated_at timestamp on row modification
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_updated_at ON public.todos;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON public.todos
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at();

-- ============================================================
-- 3. INDEXES (Performance for filtering, sorting, user queries)
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_todos_user_id    ON public.todos(user_id);
CREATE INDEX IF NOT EXISTS idx_todos_status     ON public.todos(status);
CREATE INDEX IF NOT EXISTS idx_todos_priority   ON public.todos(priority);
CREATE INDEX IF NOT EXISTS idx_todos_created_at ON public.todos(created_at DESC);

-- Composite index for common filtered queries
CREATE INDEX IF NOT EXISTS idx_todos_user_status ON public.todos(user_id, status);
CREATE INDEX IF NOT EXISTS idx_todos_user_priority ON public.todos(user_id, priority);

-- ============================================================
-- 4. ROW LEVEL SECURITY (RLS)
--    Each user can only access their own data
-- ============================================================

-- Enable RLS
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.todos ENABLE ROW LEVEL SECURITY;

-- Users table policies
DROP POLICY IF EXISTS "Users can view own profile" ON public.users;
CREATE POLICY "Users can view own profile"
    ON public.users FOR SELECT
    USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
CREATE POLICY "Users can update own profile"
    ON public.users FOR UPDATE
    USING (auth.uid() = id);

-- Todos table policies (full CRUD isolation per user)
DROP POLICY IF EXISTS "Users can view own todos" ON public.todos;
CREATE POLICY "Users can view own todos"
    ON public.todos FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can create own todos" ON public.todos;
CREATE POLICY "Users can create own todos"
    ON public.todos FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own todos" ON public.todos;
CREATE POLICY "Users can update own todos"
    ON public.todos FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own todos" ON public.todos;
CREATE POLICY "Users can delete own todos"
    ON public.todos FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================
-- 5. SERVICE ROLE BYPASS POLICY
--    Allows backend (using service_role key) to bypass RLS
--    for operations like bulk insert
-- ============================================================

DROP POLICY IF EXISTS "Service role full access to todos" ON public.todos;
CREATE POLICY "Service role full access to todos"
    ON public.todos FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

DROP POLICY IF EXISTS "Service role full access to users" ON public.users;
CREATE POLICY "Service role full access to users"
    ON public.users FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- ============================================================
-- 6. PERMISSIONS & GRANTS
--    Ensure PostgREST roles have permissions on public tables
-- ============================================================

GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL ROUTINES IN SCHEMA public TO anon, authenticated, service_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON ROUTINES TO anon, authenticated, service_role;

-- Add due_date and project if not present
ALTER TABLE public.todos ADD COLUMN IF NOT EXISTS due_date VARCHAR(50);
ALTER TABLE public.todos ADD COLUMN IF NOT EXISTS project VARCHAR(100) DEFAULT 'Inbox';

