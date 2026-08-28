<template>
  <div class="landing-container">
    <!-- ── Navigation Bar ───────────────────────────────────── -->
    <header class="landing-header">
      <div class="header-inner">
        <!-- Logo -->
        <div class="logo-group" @click="scrollToTop">
          <div class="logo-icon-box">
            <Check :size="18" :stroke-width="3" class="logo-check" />
          </div>
          <span class="logo-text">Todue </span>
        </div>

        <!-- Desktop Nav Links -->
        <nav class="desktop-nav">
          <a href="#features" class="nav-item">Features</a>
          <a href="#how-it-works" class="nav-item">How it works</a>
          <a href="#productivity" class="nav-item">Productivity</a>
          <a href="#testimonials" class="nav-item">Reviews</a>
        </nav>

        <!-- Right CTA Actions -->
        <div class="nav-actions">
          <template v-if="isAuthenticated">
            <button class="btn btn-primary btn-sm go-app-btn" @click="$emit('navigate-app')">
              <span>Go to App</span>
              <ArrowRight :size="16" />
            </button>
          </template>
          <template v-else>
            <button class="login-link-btn" @click="$emit('navigate-login')">
              Log in
            </button>
            <button class="btn btn-primary btn-sm signup-btn" @click="$emit('navigate-register')">
              Start for free
            </button>
          </template>
        </div>
      </div>
    </header>

    <!-- ── Hero Section ─────────────────────────────────────── -->
    <section class="hero-section">

      <h1 class="hero-title">
        Organize your work and life, <span class="gradient-text">finally.</span>
      </h1>

      <p class="hero-subtitle">
        Simplify your day, gain mental clarity, and achieve your goals with the world's favorite to-do list and task manager app.
      </p>

      <div class="hero-cta-group">
        <button class="hero-primary-btn" @click="handlePrimaryCta">
          <span>{{ isAuthenticated ? 'Open Your Dashboard' : 'Start for free — It’s quick' }}</span>
          <ArrowRight :size="18" />
        </button>
        <a href="#how-it-works" class="hero-secondary-btn">
          <Play :size="16" class="play-icon" />
          <span>See how it works</span>
        </a>
      </div>

      <div class="hero-guarantee">
        <div class="guarantee-item">
          <CheckCircle2 :size="14" class="guarantee-check" />
          <span>Free forever</span>
        </div>
        <div class="guarantee-item">
          <CheckCircle2 :size="14" class="guarantee-check" />
          <span>No credit card required</span>
        </div>
        <div class="guarantee-item">
          <CheckCircle2 :size="14" class="guarantee-check" />
          <span>Sync across devices</span>
        </div>
      </div>

      <!-- ── App Mockup Preview Window ──────────────────────── -->
      <div class="hero-preview-wrapper">
        <div class="mockup-window">
          <!-- Window Header Bar -->
          <div class="mockup-header-bar">
            <div class="window-dots">
              <span class="dot dot-red"></span>
              <span class="dot dot-yellow"></span>
              <span class="dot dot-green"></span>
            </div>
            <div class="window-url-bar">
              <Lock :size="12" />
              <span>app.Todue .com/app/today</span>
            </div>
            <div class="window-actions"></div>
          </div>

          <!-- Mockup App Body -->
          <div class="mockup-body">
            <!-- Mockup Sidebar -->
            <div class="mockup-sidebar">
              <div class="mockup-user">
                <div class="mockup-avatar">F</div>
                <span class="mockup-username">Frompag1928</span>
              </div>

              <div class="mockup-nav-list">
                <div class="mockup-nav-item">
                  <Inbox :size="15" />
                  <span>Inbox</span>
                  <span class="mockup-badge">3</span>
                </div>
                <div class="mockup-nav-item active">
                  <Calendar :size="15" />
                  <span>Today</span>
                  <span class="mockup-badge active">2</span>
                </div>
                <div class="mockup-nav-item">
                  <CalendarDays :size="15" />
                  <span>Upcoming</span>
                </div>
                <div class="mockup-nav-item">
                  <SlidersHorizontal :size="15" />
                  <span>Filters & Labels</span>
                </div>
              </div>

              <div class="mockup-projects-header">
                <span>My Projects</span>
              </div>
              <div class="mockup-project-item">
                <span class="project-dot-orange"></span>
                <span>Work Sprint</span>
              </div>
              <div class="mockup-project-item">
                <span class="project-dot-blue"></span>
                <span>Personal Goals</span>
              </div>
            </div>

            <!-- Mockup Main Content -->
            <div class="mockup-main">
              <div class="mockup-main-header">
                <div>
                  <h2 class="mockup-title">Today</h2>
                  <span class="mockup-subtitle">2 tasks pending</span>
                </div>
                <div class="mockup-display-tag">
                  <SlidersHorizontal :size="13" />
                  <span>Display</span>
                </div>
              </div>

              <!-- Mockup Tasks -->
              <div class="mockup-task-list">
                <div class="mockup-task done">
                  <div class="mockup-check done">
                    <Check :size="11" />
                  </div>
                  <div class="mockup-task-info">
                    <span class="mockup-task-title strikethrough">Review product architecture & API endpoints</span>
                    <span class="mockup-task-tag">Work Sprint</span>
                  </div>
                </div>

                <div class="mockup-task">
                  <div class="mockup-check p-high"></div>
                  <div class="mockup-task-info">
                    <span class="mockup-task-title">Design landing page & user onboarding workflow</span>
                    <div class="mockup-task-meta">
                      <span class="tag-priority high">P1 High</span>
                      <span class="mockup-task-tag">Work Sprint</span>
                    </div>
                  </div>
                </div>

                <div class="mockup-task">
                  <div class="mockup-check p-med"></div>
                  <div class="mockup-task-info">
                    <span class="mockup-task-title">Plan weekly workout routine & grocery list</span>
                    <div class="mockup-task-meta">
                      <span class="tag-priority med">P2 Medium</span>
                      <span class="mockup-task-tag">Personal Goals</span>
                    </div>
                  </div>
                </div>

                <div class="mockup-add-task">
                  <Plus :size="14" class="mockup-add-icon" />
                  <span>Add task</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Social Proof & Metrics ───────────────────────────── -->
    <section class="metrics-section">
      <div class="metrics-container">
        <p class="metrics-intro">Loved by over 30 million individuals and high-performing teams worldwide</p>
        <div class="metrics-grid">
          <div class="metric-card">
            <span class="metric-number">30M+</span>
            <span class="metric-label">Active Creators & Teams</span>
          </div>
          <div class="metric-card">
            <span class="metric-number">2 Billion+</span>
            <span class="metric-label">Tasks Completed</span>
          </div>
          <div class="metric-card">
            <span class="metric-number">4.8 / 5</span>
            <span class="metric-label">App Store & Google Play</span>
          </div>
          <div class="metric-card">
            <span class="metric-number">99.9%</span>
            <span class="metric-label">Uptime & Cloud Sync</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Core Features Section ────────────────────────────── -->
    <section id="features" class="features-section">
      <div class="section-header">
        <span class="section-tag">Powerful Features</span>
        <h2 class="section-title">Everything you need to master your day</h2>
        <p class="section-desc">Designed with simplicity and immense speed so you spend less time planning and more time doing.</p>
      </div>

      <div class="features-grid">
        <!-- Feature 1 -->
        <div class="feature-card">
          <div class="feature-icon-box bg-red">
            <Zap :size="22" />
          </div>
          <h3 class="feature-title">Lightning-Fast Quick Add</h3>
          <p class="feature-text">
            Capture thoughts instantly with intelligent inline creation, preset due dates, priorities, and project tags.
          </p>
        </div>

        <!-- Feature 2 -->
        <div class="feature-card">
          <div class="feature-icon-box bg-blue">
            <Calendar :size="22" />
          </div>
          <h3 class="feature-title">Today & Upcoming Views</h3>
          <p class="feature-text">
            Never miss a deadline. Visualize your full schedule day by day with the interactive upcoming week timeline.
          </p>
        </div>

        <!-- Feature 3 -->
        <div class="feature-card">
          <div class="feature-icon-box bg-orange">
            <Layers :size="22" />
          </div>
          <h3 class="feature-title">Projects & Priorities</h3>
          <p class="feature-text">
            Categorize your life into work, personal, and study. Highlight what matters most using color-coded priority flags.
          </p>
        </div>

        <!-- Feature 4 -->
        <div class="feature-card">
          <div class="feature-icon-box bg-green">
            <TrendingUp :size="22" />
          </div>
          <h3 class="feature-title">Productivity & Karma Stats</h3>
          <p class="feature-text">
            Track your daily streaks, completion rates, and celebrate achieving a 100% finished week.
          </p>
        </div>
      </div>
    </section>

    <!-- ── How It Works Interactive Showcase ────────────────── -->
    <section id="how-it-works" class="showcase-section">
      <div class="section-header">
        <span class="section-tag">How It Works</span>
        <h2 class="section-title">From brain dump to done in seconds</h2>
        <p class="section-desc">Three simple steps to regain control of your schedule.</p>
      </div>

      <div class="steps-grid">
        <div class="step-card">
          <div class="step-number">01</div>
          <h3 class="step-title">Capture your tasks</h3>
          <p class="step-text">Type anything on your mind. Assign due dates like Today, Tomorrow, or next week with one click.</p>
        </div>
        <div class="step-card">
          <div class="step-number">02</div>
          <h3 class="step-title">Focus on Today</h3>
          <p class="step-text">Open your Today view to see exactly what needs your attention right now, free from distractions.</p>
        </div>
        <div class="step-card">
          <div class="step-number">03</div>
          <h3 class="step-title">Check off & Celebrate</h3>
          <p class="step-text">Mark tasks done with 0ms instant feedback and watch your completion streak grow day by day.</p>
        </div>
      </div>
    </section>

    <!-- ── Testimonials ─────────────────────────────────────── -->
    <section id="testimonials" class="testimonials-section">
      <div class="section-header">
        <span class="section-tag">User Stories</span>
        <h2 class="section-title">Why millions choose our task manager</h2>
      </div>

      <div class="testimonials-grid">
        <div class="testimonial-card">
          <p class="testimonial-quote">
            "Todue  has completely transformed how I run my design agency. It keeps our daily sprints laser-focused and stress-free."
          </p>
          <div class="testimonial-author">
            <div class="author-avatar">A</div>
            <div class="author-details">
              <span class="author-name">Alex Rivera</span>
              <span class="author-role">Product Lead @ Horizon</span>
            </div>
          </div>
        </div>

        <div class="testimonial-card">
          <p class="testimonial-quote">
            "The Today & Upcoming views are unmatched. I finally feel in control of my university assignments and personal projects."
          </p>
          <div class="testimonial-author">
            <div class="author-avatar bg-purple">S</div>
            <div class="author-details">
              <span class="author-name">Sarah Chen</span>
              <span class="author-role">Computer Science Student</span>
            </div>
          </div>
        </div>

        <div class="testimonial-card">
          <p class="testimonial-quote">
            "Zero delay, beautiful minimalist interface, and instant sync. The best productivity investment I've made this year."
          </p>
          <div class="testimonial-author">
            <div class="author-avatar bg-amber">M</div>
            <div class="author-details">
              <span class="author-name">Marcus Vance</span>
              <span class="author-role">Engineering Manager</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Call to Action Banner ────────────────────────────── -->
    <section class="cta-banner-section">
      <div class="cta-banner-card">
        <h2 class="cta-title">Gain clarity and calm in your day.</h2>
        <p class="cta-subtitle">Join over 30 million people who conquer their goals every single day with Todue .</p>
        <button class="cta-banner-btn" @click="handlePrimaryCta">
          <span>{{ isAuthenticated ? 'Go to Your Dashboard' : 'Get Started — It’s Free' }}</span>
          <ArrowRight :size="18" />
        </button>
      </div>
    </section>

    <!-- ── Footer ───────────────────────────────────────────── -->
    <footer class="landing-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <div class="logo-group">
            <div class="logo-icon-box">
              <Check :size="16" :stroke-width="3" class="logo-check" />
            </div>
            <span class="logo-text">Todue </span>
          </div>
          <p class="footer-tagline">Organize your work and life, finally.</p>
        </div>

        <div class="footer-links-group">
          <div class="footer-col">
            <span class="footer-heading">Features</span>
            <a href="#features" class="footer-link">How it Works</a>
            <a href="#productivity" class="footer-link">Upcoming View</a>
            <a href="#features" class="footer-link">Priorities</a>
          </div>
          <div class="footer-col">
            <span class="footer-heading">Resources</span>
            <a href="#how-it-works" class="footer-link">Productivity Guide</a>
            <a href="#testimonials" class="footer-link">Customer Reviews</a>
            <a href="#features" class="footer-link">Keyboard Shortcuts</a>
          </div>
          <div class="footer-col">
            <span class="footer-heading">Account</span>
            <button class="footer-btn-link" @click="$emit('navigate-login')">Log in</button>
            <button class="footer-btn-link" @click="$emit('navigate-register')">Create free account</button>
          </div>
        </div>
      </div>

      <div class="footer-bottom">
        <span>© 2026 Todue  Clone. Built with Vue 3 & FastAPI. All rights reserved.</span>
        <div class="footer-status">
          <span class="status-dot"></span>
          <span>All systems operational</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import {
  Check,
  ArrowRight,
  Sparkles,
  Play,
  CheckCircle2,
  Lock,
  Inbox,
  Calendar,
  CalendarDays,
  SlidersHorizontal,
  Plus,
  Zap,
  Layers,
  TrendingUp,
} from 'lucide-vue-next'

const props = defineProps({
  isAuthenticated: Boolean,
})

const emit = defineEmits([
  'navigate-login',
  'navigate-register',
  'navigate-app',
])

function handlePrimaryCta() {
  if (props.isAuthenticated) {
    emit('navigate-app')
  } else {
    emit('navigate-register')
  }
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<style scoped>
.landing-container {
  min-height: 100vh;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-family-base);
  overflow-x: hidden;
}

/* ── Navbar ─────────────────────────────────────────────── */
.landing-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-light);
  transition: all var(--transition-fast);
}

[data-theme="dark"] .landing-header {
  background: rgba(31, 31, 31, 0.9);
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-group {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.logo-icon-box {
  width: 32px;
  height: 32px;
  border-radius: var(--border-radius-sm);
  background: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(220, 76, 62, 0.3);
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: -0.02em;
}

.desktop-nav {
  display: flex;
  align-items: center;
  gap: 28px;
}

.nav-item {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.nav-item:hover {
  color: var(--text-primary);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.login-link-btn {
  background: transparent;
  border: none;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  cursor: pointer;
  padding: 8px 12px;
  border-radius: var(--border-radius-sm);
  transition: background var(--transition-fast);
}

.login-link-btn:hover {
  background: var(--bg-hover);
}

.signup-btn,
.go-app-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  padding: 8px 18px;
}

/* ── Hero Section ───────────────────────────────────────── */
.hero-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 24px 80px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: rgba(220, 76, 62, 0.08);
  border: 1px solid rgba(220, 76, 62, 0.2);
  border-radius: var(--border-radius-full);
  color: var(--color-primary);
  font-size: var(--font-size-xs);
  font-weight: 600;
  margin-bottom: 24px;
}

.hero-title {
  font-size: 56px;
  font-weight: 800;
  line-height: 1.12;
  letter-spacing: -0.03em;
  color: var(--text-primary);
  max-width: 820px;
  margin-bottom: 20px;
}

.gradient-text {
  color: var(--color-primary);
}

.hero-subtitle {
  font-size: 19px;
  line-height: 1.5;
  color: var(--text-secondary);
  max-width: 660px;
  margin-bottom: 36px;
}

.hero-cta-group {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.hero-primary-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  background: var(--color-primary);
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  border-radius: var(--border-radius-md);
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(220, 76, 62, 0.35);
  transition: all var(--transition-fast);
}

.hero-primary-btn:hover {
  background: var(--color-primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(220, 76, 62, 0.45);
}

.hero-secondary-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 24px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  color: var(--text-primary);
  font-size: 15px;
  font-weight: 600;
  border-radius: var(--border-radius-md);
  text-decoration: none;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.hero-secondary-btn:hover {
  background: var(--bg-hover);
}

.play-icon {
  color: var(--color-primary);
}

.hero-guarantee {
  display: flex;
  align-items: center;
  gap: 24px;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  margin-bottom: 50px;
  flex-wrap: wrap;
  justify-content: center;
}

.guarantee-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.guarantee-check {
  color: #058527;
}

/* ── App Mockup Preview Window ──────────────────────────── */
.hero-preview-wrapper {
  width: 100%;
  max-width: 960px;
  margin: 0 auto;
  border-radius: var(--border-radius-lg);
  box-shadow: 0 20px 60px -15px rgba(0, 0, 0, 0.15), 0 0 0 1px var(--border-light);
  overflow: hidden;
  background: var(--bg-surface);
  text-align: left;
}

.mockup-header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 18px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-light);
}

.window-dots {
  display: flex;
  gap: 7px;
}

.dot {
  width: 11px;
  height: 11px;
  border-radius: 50%;
}

.dot-red { background: #ff5f56; }
.dot-yellow { background: #ffbd2e; }
.dot-green { background: #27c93f; }

.window-url-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 16px;
  background: var(--bg-surface);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  border: 1px solid var(--border-light);
}

.mockup-body {
  display: flex;
  min-height: 380px;
}

.mockup-sidebar {
  width: 220px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-light);
  padding: 16px 12px;
}

.mockup-user {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 18px;
  padding: 4px 8px;
}

.mockup-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #058527;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mockup-username {
  font-size: 13px;
  font-weight: 600;
}

.mockup-nav-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 20px;
}

.mockup-nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  border-radius: var(--border-radius-sm);
  font-size: 13px;
  color: var(--text-secondary);
}

.mockup-nav-item.active {
  background: var(--bg-hover);
  color: var(--color-primary);
  font-weight: 600;
}

.mockup-badge {
  margin-left: auto;
  font-size: 11px;
  color: var(--text-tertiary);
}

.mockup-badge.active {
  color: var(--color-primary);
  font-weight: 600;
}

.mockup-projects-header {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-tertiary);
  padding: 0 10px;
  margin-bottom: 8px;
}

.mockup-project-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 10px;
  font-size: 13px;
  color: var(--text-secondary);
}

.project-dot-orange { width: 7px; height: 7px; border-radius: 50%; background: #eb8909; }
.project-dot-blue { width: 7px; height: 7px; border-radius: 50%; background: #246fe0; }

.mockup-main {
  flex: 1;
  padding: 24px 32px;
}

.mockup-main-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 20px;
}

.mockup-title {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 2px;
}

.mockup-subtitle {
  font-size: 12px;
  color: var(--text-tertiary);
}

.mockup-display-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  padding: 4px 8px;
  border: 1px solid var(--border-default);
  border-radius: var(--border-radius-sm);
  color: var(--text-secondary);
}

.mockup-task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mockup-task {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-light);
  border-radius: var(--border-radius-sm);
  background: var(--bg-surface);
}

.mockup-check {
  width: 17px;
  height: 17px;
  min-width: 17px;
  border-radius: 50%;
  border: 1.5px solid var(--text-tertiary);
  margin-top: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mockup-check.done {
  background: var(--status-done);
  border-color: var(--status-done);
  color: #fff;
}

.mockup-check.p-high { border-color: var(--priority-high); }
.mockup-check.p-med { border-color: var(--priority-medium); }

.mockup-task-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mockup-task-title {
  font-size: 13.5px;
  color: var(--text-primary);
  font-weight: 500;
}

.mockup-task-title.strikethrough {
  text-decoration: line-through;
  color: var(--text-tertiary);
}

.mockup-task-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tag-priority {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}

.tag-priority.high { background: var(--priority-high-bg); color: var(--priority-high); }
.tag-priority.med { background: var(--priority-medium-bg); color: var(--priority-medium); }

.mockup-task-tag {
  font-size: 11px;
  color: var(--text-tertiary);
}

.mockup-add-task {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 4px;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}

/* ── Metrics Band ───────────────────────────────────────── */
.metrics-section {
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-light);
  border-bottom: 1px solid var(--border-light);
  padding: 50px 24px;
}

.metrics-container {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.metrics-intro {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 36px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.metric-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.metric-number {
  font-size: 38px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.metric-label {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  font-weight: 500;
}

/* ── Features Grid ──────────────────────────────────────── */
.features-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 100px 24px;
}

.section-header {
  text-align: center;
  max-width: 640px;
  margin: 0 auto 60px;
}

.section-tag {
  font-size: var(--font-size-xs);
  font-weight: 700;
  text-transform: uppercase;
  color: var(--color-primary);
  letter-spacing: 0.06em;
  display: block;
  margin-bottom: 8px;
}

.section-title {
  font-size: 36px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
  margin-bottom: 12px;
}

.section-desc {
  font-size: var(--font-size-base);
  color: var(--text-secondary);
  line-height: 1.5;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.feature-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--border-radius-lg);
  padding: 28px 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: all var(--transition-fast);
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary);
}

.feature-icon-box {
  width: 46px;
  height: 46px;
  border-radius: var(--border-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-bottom: 8px;
}

.bg-red { background: var(--color-primary); }
.bg-blue { background: #246fe0; }
.bg-orange { background: #eb8909; }
.bg-green { background: #058527; }

.feature-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.feature-text {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.5;
}

/* ── How It Works ───────────────────────────────────────── */
.showcase-section {
  background: var(--bg-secondary);
  padding: 90px 24px;
}

.steps-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
}

.step-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--border-radius-lg);
  padding: 32px 28px;
}

.step-number {
  font-size: 28px;
  font-weight: 800;
  color: var(--color-primary);
  opacity: 0.8;
  margin-bottom: 14px;
}

.step-title {
  font-size: 19px;
  font-weight: 700;
  margin-bottom: 8px;
}

.step-text {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.6;
}

/* ── Testimonials ───────────────────────────────────────── */
.testimonials-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 100px 24px;
}

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.testimonial-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--border-radius-lg);
  padding: 28px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 20px;
}

.testimonial-quote {
  font-size: var(--font-size-sm);
  line-height: 1.6;
  color: var(--text-secondary);
  font-style: italic;
}

.testimonial-author {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #246fe0;
  color: #fff;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.author-avatar.bg-purple { background: #7c3aed; }
.author-avatar.bg-amber { background: #d97706; }

.author-details {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-size: var(--font-size-sm);
  font-weight: 700;
  color: var(--text-primary);
}

.author-role {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

/* ── Call To Action Banner ──────────────────────────────── */
.cta-banner-section {
  max-width: 1200px;
  margin: 0 auto 90px;
  padding: 0 24px;
}

.cta-banner-card {
  background: linear-gradient(135deg, #e65a4c 0%, #dc4c3e 100%);
  border-radius: var(--border-radius-lg);
  padding: 60px 32px;
  text-align: center;
  color: #ffffff;
  box-shadow: 0 16px 40px rgba(220, 76, 62, 0.3);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.cta-title {
  font-size: 38px;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-bottom: 12px;
}

.cta-subtitle {
  font-size: 17px;
  opacity: 0.95;
  max-width: 600px;
  margin-bottom: 30px;
  line-height: 1.5;
}

.cta-banner-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 32px;
  background: #ffffff;
  color: var(--color-primary);
  font-size: 16px;
  font-weight: 700;
  border-radius: var(--border-radius-md);
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all var(--transition-fast);
}

.cta-banner-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.2);
}

/* ── Footer ─────────────────────────────────────────────── */
.landing-footer {
  background: var(--bg-surface);
  border-top: 1px solid var(--border-light);
  padding: 60px 24px 30px;
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto 50px;
  display: flex;
  justify-content: space-between;
  gap: 40px;
  flex-wrap: wrap;
}

.footer-brand {
  max-width: 300px;
}

.footer-tagline {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  margin-top: 10px;
}

.footer-links-group {
  display: flex;
  gap: 60px;
  flex-wrap: wrap;
}

.footer-col {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.footer-heading {
  font-size: var(--font-size-xs);
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.footer-link {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.footer-link:hover {
  color: var(--color-primary);
}

.footer-btn-link {
  background: transparent;
  border: none;
  text-align: left;
  padding: 0;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: color var(--transition-fast);
}

.footer-btn-link:hover {
  color: var(--color-primary);
}

.footer-bottom {
  max-width: 1200px;
  margin: 0 auto;
  padding-top: 24px;
  border-top: 1px solid var(--border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  flex-wrap: wrap;
  gap: 12px;
}

.footer-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #27c93f;
}

/* ── Responsive ─────────────────────────────────────────── */
@media (max-width: 1024px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .mockup-body {
    flex-direction: column;
  }

  .mockup-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--border-light);
  }
}

@media (max-width: 768px) {
  .desktop-nav {
    display: none;
  }

  .hero-title {
    font-size: 38px;
  }

  .hero-subtitle {
    font-size: 16px;
  }

  .steps-grid,
  .testimonials-grid {
    grid-template-columns: 1fr;
  }

  .features-grid,
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
