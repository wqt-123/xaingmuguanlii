import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory('/qingtian/'),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/',
      component: () => import('@/components/layout/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/dashboard' },
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/DashboardView.vue'),
        },
        {
          path: 'plans',
          name: 'Plans',
          component: () => import('@/views/PlanListView.vue'),
        },
        {
          path: 'plans/:id',
          name: 'PlanDetail',
          component: () => import('@/views/PlanDetailView.vue'),
        },
        {
          path: 'gantt/:planId?',
          name: 'Gantt',
          component: () => import('@/views/GanttView.vue'),
        },
        {
          path: 'requirements',
          name: 'Requirements',
          component: () => import('@/views/RequirementListView.vue'),
        },
        {
          path: 'requirements/:id',
          name: 'RequirementDetail',
          component: () => import('@/views/RequirementDetailView.vue'),
        },
        {
          path: 'defects',
          name: 'Defects',
          component: () => import('@/views/DefectListView.vue'),
        },
        {
          path: 'defects/:id',
          name: 'DefectDetail',
          component: () => import('@/views/DefectDetailView.vue'),
        },
        {
          path: 'team',
          name: 'Team',
          component: () => import('@/views/TeamView.vue'),
        },
        {
          path: 'inbox',
          name: 'Inbox',
          component: () => import('@/views/InboxView.vue'),
        },
      ],
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const token = sessionStorage.getItem('atlas-token')
  if (to.meta.requiresAuth && !token) next('/login')
  else if (to.path === '/login' && token) next('/dashboard')
  else next()
})

export default router
