<template>
  <div class="space-y-6">
    <button @click="$router.push('/defects')" class="text-sm text-cockpit-gold hover:text-cockpit-accent transition-colors">← 返回缺陷列表</button>
    <div v-if="defect" class="glass-panel p-6">
      <div class="flex justify-between items-start mb-4">
        <div><span class="text-xs text-cockpit-muted">BUG-{{ defect.id }}</span><h2 class="text-xl font-bold mt-1">{{ defect.title }}</h2></div>
        <span class="px-3 py-1 rounded text-xs font-semibold" :class="severityBadge(defect.severity)">{{ severityLabel(defect.severity) }}</span>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 text-sm">
        <div><span class="text-cockpit-muted">状态: </span><span :class="statusBadge(defect.status)">{{ statusLabel(defect.status) }}</span></div>
        <div><span class="text-cockpit-muted">严重程度: </span>{{ severityLabel(defect.severity) }}</div>
        <div><span class="text-cockpit-muted">优先级: </span>{{ defect.priority }}</div>
        <div><span class="text-cockpit-muted">模块: </span>{{ defect.module || '-' }}</div>
        <div><span class="text-cockpit-muted">发现版本: </span>{{ defect.found_version || '-' }}</div>
        <div><span class="text-cockpit-muted">环境: </span>{{ defect.environment || '-' }}</div>
      </div>
      <div class="mb-4"><h4 class="text-sm font-semibold text-cockpit-gold mb-2">缺陷描述</h4><p class="text-sm text-cockpit-muted whitespace-pre-wrap">{{ defect.description || '暂无描述' }}</p></div>
      <div v-if="defect.repro_steps" class="mb-4"><h4 class="text-sm font-semibold text-cockpit-gold mb-2">复现步骤</h4><p class="text-sm text-cockpit-muted whitespace-pre-wrap">{{ defect.repro_steps }}</p></div>
      <!-- Workflow actions -->
      <div class="flex flex-wrap gap-2 border-t border-cockpit-border/20 pt-4">
        <button v-for="action in availableActions" :key="action" @click="changeStatus(action)"
          class="px-3 py-1.5 rounded text-xs font-semibold transition-all"
          :class="actionColor(action)">{{ actionLabel(action) }}</button>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'; import { useRoute } from 'vue-router'; import api from '@/api/client'
const route = useRoute(); const defect = ref<any>(null)
const flowMap: Record<string, string[]> = {
  new: ['assigned'], assigned: ['fixing'], fixing: ['fixed'],
  fixed: ['verified','reopened'], verified: ['closed','reopened'], closed: ['reopened'], reopened: ['assigned']
}
const availableActions = computed(() => flowMap[defect.value?.status] || [])
const statusLabel=(s:string)=>({new:'新建',assigned:'已分配',fixing:'修复中',fixed:'已修复',verified:'已验证',closed:'已关闭',reopened:'重新打开'}[s]||s)
const statusBadge=(s:string)=>({new:'badge-todo',fixed:'badge-done',closed:'badge-done',verified:'badge-done',reopened:'badge-urgent',fixing:'badge-progress',assigned:'badge-high'}[s]||'badge-todo')
const severityLabel=(s:string)=>({critical:'致命',major:'严重',minor:'轻微',trivial:'建议'}[s]||s)
const severityBadge=(s:string)=>({critical:'badge-urgent',major:'badge-high',minor:'badge-todo',trivial:'badge-progress'}[s]||'badge-todo')
const actionLabel=(a:string)=>({assigned:'分配',fixing:'开始修复',fixed:'标记已修复',verified:'验证通过',closed:'关闭',reopened:'重新打开'}[a]||a)
const actionColor=(a:string)=>({closed:'bg-green-500/20 text-green-400 hover:bg-green-500/30',verified:'bg-green-500/20 text-green-400',fixed:'bg-blue-500/20 text-blue-400',reopened:'bg-red-500/20 text-red-400',assigned:'bg-yellow-500/20 text-yellow-400',fixing:'bg-purple-500/20 text-purple-400'}[a]||'bg-white/10 text-cockpit-muted')
onMounted(async()=>{try{const id=route.params.id as string;const r:any=await api.get('/defects/'+id);defect.value=r.data}catch{}})
async function changeStatus(status:string){try{const id=route.params.id as string;await api.patch('/defects/'+id+'/status',{status});defect.value.status=status}catch{}}
</script>
