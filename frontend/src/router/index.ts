import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
    },
{
      path: '/dashboard/admin',
      name: 'admin-dashboard',
      component: () => import('../views/AdminDashboardView.vue'),
    },
    {
      path: '/dashboard/patient',
      name: 'patient-dashboard',
      component: () => import('../views/PatientDashboardView.vue'),
    },
    {
      path: '/dashboard/provider',
      name: 'provider-dashboard',
      component: () => import('../views/ProviderDashboardView.vue'),
    },
  ],
})

router.beforeEach((to, from, next) => {
  const user = localStorage.getItem('user')
 const role = localStorage.getItem('role')

  if (to.path.startsWith('/dashboard') && !user) {
    next('/login')
    return
  }

  if (to.path === '/dashboard/admin' && role !== 'admin') {
    next('/login')
    return
  }

  if (to.path === '/dashboard/provider' && role !== 'provider') {
    next('/login')
    return
  }

  if (to.path === '/dashboard/patient' && role !== 'patient') {
    next('/login')
    return
  }

  next()
})

export default router
