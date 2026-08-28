import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Landing',
    meta: { public: true },
  },
  {
    path: '/app',
    name: 'Dashboard',
    meta: { requiresAuth: true },
  },
  {
    path: '/login',
    name: 'Login',
    meta: { guestOnly: true, mode: 'login' },
  },
  {
    path: '/register',
    name: 'Register',
    meta: { guestOnly: true, mode: 'register' },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const user = localStorage.getItem('user')
  const isAuthenticated = !!token && !!user

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.guestOnly && isAuthenticated) {
    next('/app')
  } else {
    next()
  }
})

export default router
