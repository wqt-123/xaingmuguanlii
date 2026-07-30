<template>
  <aside class="w-64 flex-shrink-0 border-r border-cockpit-border/20 flex flex-col h-full"
    style="background: linear-gradient(180deg, rgba(17,24,39,0.95) 0%, rgba(10,14,23,0.98) 100%)">
    <div class="p-5 border-b border-cockpit-border/20">
      <h1 class="text-xl font-bold text-glow tracking-wider">深入云境-Nick</h1>
      <p class="text-xs text-cockpit-muted mt-1">作战驾驶舱</p>
    </div>
    <nav class="flex-1 p-3 space-y-1 overflow-auto">
      <router-link v-for="item in navItems" :key="item.to" :to="item.to"
        class="nav-item flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-300 relative overflow-hidden"
        :class="$route.path.startsWith(item.to) && item.to !== '/' ? 'nav-active' : 'text-cockpit-muted'">
        <!-- Hover/Active background layer -->
        <div class="absolute inset-0 nav-bg" />
        <span class="relative z-10 text-lg">{{ item.icon }}</span>
        <span class="relative z-10">{{ item.label }}</span>
        <!-- Active indicator bar -->
        <div v-if="$route.path.startsWith(item.to) && item.to !== '/'"
          class="absolute left-0 top-1.5 bottom-1.5 w-0.5 rounded-full bg-blue-400 shadow-[0_0_8px_rgba(96,165,250,0.6)] nav-indicator" />
      </router-link>
    </nav>
    <div class="p-4 border-t border-cockpit-border/20">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-full bg-cockpit-accent/20 flex items-center justify-center text-sm text-cockpit-accent font-bold">
          {{ userInitial }}
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium truncate">{{ userName }}</p>
          <p class="text-xs text-cockpit-muted">{{ userRole }}</p>
        </div>
        <button @click="logout" class="text-cockpit-muted hover:text-cockpit-accent transition-colors" title="退出">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const navItems = [
  { to: '/dashboard', icon: '◉', label: '仪表盘' },
  { to: '/projects', icon: '📁', label: '项目管理' },
  { to: '/gantt', icon: '≣', label: '甘特图' },
  { to: '/requirements', icon: '☰', label: '需求管理' },
  { to: '/defects', icon: '⚠', label: '缺陷管理' },
  { to: '/mytasks', icon: '📋', label: '我的任务' },
  { to: '/team', icon: '👥', label: '团队管理' },
  { to: '/inbox', icon: '✉', label: '消息中心' },
  { to: '/settings', icon: '⚙', label: '个人设置' },
]

const userInitial = computed(() => (auth.user?.name || 'U')[0].toUpperCase())
const userName = computed(() => auth.user?.name || '用户')
const userRole = computed(() => auth.user?.role === 'admin' ? '管理员' : '成员')

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.nav-item {
  position: relative;
}
.nav-item .nav-bg {
  background: transparent;
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
  transform: scale(0.9);
  opacity: 0;
}
.nav-item:hover .nav-bg {
  background: rgba(255,255,255,0.06);
  transform: scale(1);
  opacity: 1;
}
.nav-item:hover {
  transform: scale(1.03);
}
.nav-active {
  background: linear-gradient(135deg, rgba(59,130,246,0.2) 0%, rgba(96,165,250,0.12) 100%) !important;
  color: #60A5FA !important;
  font-weight: 600;
  transform: scale(1.04);
  border: 1px solid rgba(96,165,250,0.35);
  box-shadow: 0 0 16px rgba(59,130,246,0.15), inset 0 0 8px rgba(59,130,246,0.06);
}
.nav-active:hover {
  transform: scale(1.06);
}
.nav-indicator {
  animation: indicatorIn 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}
@keyframes indicatorIn {
  from { transform: scaleY(0); opacity: 0; }
  to { transform: scaleY(1); opacity: 1; }
}
</style>
