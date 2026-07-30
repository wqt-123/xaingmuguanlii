<template>
  <header class="h-14 flex items-center justify-between px-6 border-b border-cockpit-border/20"
    style="background: linear-gradient(180deg, rgba(17,24,39,0.9) 0%, rgba(17,24,39,0.6) 100%)">
    <div class="flex items-center gap-4">
      <span class="text-sm text-cockpit-muted">
        {{ currentPage }}
      </span>
    </div>
    <div class="flex items-center gap-3">
      <button class="relative p-2 text-cockpit-muted hover:text-cockpit-gold transition-colors rounded-lg hover:bg-white/5">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
        <span v-if="unreadCount" class="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full bg-cockpit-accent text-[10px] flex items-center justify-center animate-pulse">{{ unreadCount }}</span>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/client'

const route = useRoute()
const unreadCount = ref(0)
onMounted(async()=>{try{const r:any=await api.get('/messages/unread-count');unreadCount.value=r.data?.count||0}catch{}})

const pageNames: Record<string, string> = {
  dashboard: '仪表盘', projects: '项目管理', plans: '项目管理', gantt: '甘特图',
  requirements: '需求管理', defects: '缺陷管理',
  mytasks: '我的任务', team: '团队管理', inbox: '消息中心', settings: '个人设置',
}

const currentPage = computed(() => {
  const name = route.name as string
  return pageNames[name] || name || '仪表盘'
})
</script>
