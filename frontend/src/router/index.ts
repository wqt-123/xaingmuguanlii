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
        { path: 'plans', redirect: '/projects' },
        { path: 'plans/:id', redirect: (to: any) => `/projects/${to.params.id}` },
        {
          path: 'projects',
          name: 'Projects',
          component: () => import('@/views/PlanListView.vue'),
        },
        {
          path: 'projects/:id',
          name: 'ProjectDetail',
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
        {
          path: 'mytasks',
          name: 'MyTasks',
          component: () => import('@/views/MyTasksView.vue'),
        },
        {
          path: 'settings',
          name: 'Settings',
          component: () => import('@/views/SettingsView.vue'),
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
