<template>
  <div class="space-y-4">
    <h2 class="text-2xl font-bold text-glow">我的任务</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="col in columns" :key="col.key" class="glass-panel p-3 min-h-[300px]">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm font-semibold" :class="col.color">{{ col.label }}</h3>
          <span class="text-xs px-2 py-0.5 rounded-full bg-white/10">{{ colTasks(col.key).length }}</span>
        </div>
        <div class="space-y-2">
          <div v-for="t in colTasks(col.key)" :key="t.id" draggable="true" @dragstart="dragTask=t;col.key"
            @click="showDetail=t"
            class="p-3 rounded-lg border cursor-pointer transition-all hover:scale-[1.02]"
            :class="[col.border, isOverdue(t) ? 'border-cockpit-accent/50 bg-cockpit-accent/8 alert-pulse-border' : 'border-cockpit-border/20 bg-white/3']">
            <p class="text-sm font-medium mb-1.5">{{ t.title }}</p>
            <div class="flex flex-wrap gap-1 text-[10px] text-cockpit-muted">
              <span class="px-1.5 py-0.5 rounded bg-white/10">{{ t.project_name || '项目'+t.project_id }}</span>
              <span>⏱ {{ t.estimated_hours || 0 }}h</span>
            </div>
            <div class="flex justify-between items-center mt-2 text-[10px]">
              <span :class="isOverdue(t) ? 'text-cockpit-accent' : 'text-cockpit-muted'">
                {{ isOverdue(t) ? '⚠ 逾期' : '📅 ' + formatDate(t.end_date) }}
              </span>
              <span class="px-1.5 py-0.5 rounded" :class="priorityBadge(t.priority)">{{ t.priority }}</span>
            </div>
          </div>
          <p v-if="colTasks(col.key).length===0" class="text-[10px] text-cockpit-muted text-center py-6">拖拽任务至此</p>
        </div>
        <!-- Drop zone -->
        <div class="mt-2 h-10 rounded-lg border border-dashed border-cockpit-border/20 flex items-center justify-center text-[10px] text-cockpit-muted transition-all hover:border-cockpit-gold/40"
          @dragover.prevent @drop.prevent="handleDrop(col.key)">释放到「{{ col.label }}」</div>
      </div>
    </div>
    <!-- Task Detail -->
    <div v-if="showDetail" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50" @click.self="showDetail=null">
      <div class="glass-panel p-6 w-full max-w-lg mx-4 animate-slide-up">
        <h3 class="text-lg font-semibold mb-1">{{ showDetail.title }}</h3>
        <p class="text-xs text-cockpit-muted mb-4">{{ showDetail.description || '暂无描述' }}</p>
        <div class="grid grid-cols-2 gap-3 text-sm mb-4">
          <div><span class="text-cockpit-muted">状态: </span>{{ statusLabel(showDetail.status) }}</div>
          <div><span class="text-cockpit-muted">优先级: </span>{{ showDetail.priority }}</div>
          <div><span class="text-cockpit-muted">开始: </span>{{ formatDate(showDetail.start_date) }}</div>
          <div><span class="text-cockpit-muted">截止: </span>{{ formatDate(showDetail.end_date) }}</div>
          <div><span class="text-cockpit-muted">计划工时: </span>{{ showDetail.estimated_hours || 0 }}h</div>
          <div><span class="text-cockpit-muted">实际工时: </span>{{ showDetail.actual_hours || 0 }}h</div>
        </div>
        <div class="flex gap-2 border-t border-cockpit-border/20 pt-4">
          <select @change="changeStatus(($event.target as HTMLSelectElement).value)" class="text-xs px-2 py-1 bg-white/5 border border-cockpit-border/30 rounded">
            <option value="">切换状态</option>
            <option v-for="c in columns" :key="c.key" :value="c.key">{{ c.label }}</option>
          </select>
          <button @click="showDetail=null" class="ml-auto px-3 py-1 bg-white/10 rounded text-xs">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'; import api from '@/api/client'

const columns = [
  { key: 'todo', label: '待办', color: 'text-slate-400', border: 'border-slate-500/20' },
  { key: 'pending', label: '待处理', color: 'text-yellow-400', border: 'border-yellow-500/20' },
  { key: 'in_progress', label: '进行中', color: 'text-blue-400', border: 'border-blue-500/20' },
  { key: 'done', label: '已完成', color: 'text-green-400', border: 'border-green-500/20' },
]

const allTasks = ref<any[]>([]); const showDetail = ref<any>(null); const dragTask = ref<any>(null)

const statusLabel=(s:string)=>({todo:'待办',pending:'待处理',in_progress:'进行中',done:'已完成',review:'审核中',blocked:'阻塞'}[s]||s)
const priorityBadge=(p:string)=>({urgent:'badge-urgent',high:'badge-high',medium:'badge-todo',low:'badge-progress'}[p]||'badge-todo')
const formatDate=(d:string)=>d ? d.split('T')[0] : '-'
const isOverdue=(t:any)=>t.end_date && new Date(t.end_date) < new Date() && t.status !== 'done'
const colTasks=(key:string)=>allTasks.value.filter((t:any)=>t.status===key).slice(0,10)

onMounted(async()=>{try{const r:any=await api.get('/tasks/my');allTasks.value=r.data||[]}catch{}})

async function handleDrop(status:string) {
  if (!dragTask.value) return
  try { await api.patch(`/tasks/${dragTask.value.id}/status`,{status}); dragTask.value.status = status } catch {}
}

async function changeStatus(status:string) {
  if (!status || !showDetail.value) return
  try { await api.patch(`/tasks/${showDetail.value.id}/status`,{status}); showDetail.value.status = status; showDetail.value = null } catch {}
}
</script>
