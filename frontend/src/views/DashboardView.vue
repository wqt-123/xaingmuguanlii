<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-bold text-glow">作战总览</h2>
    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      <div v-for="card in kpiCards" :key="card.label"
        class="glass-panel p-4 text-center cursor-pointer hover:scale-[1.02] transition-transform"
        @click="$router.push(card.link)">
        <p class="text-xs text-cockpit-muted mb-1">{{ card.label }}</p>
        <p class="text-3xl font-bold text-glow-accent">{{ card.value }}</p>
        <p v-if="card.sub" class="text-[10px] text-cockpit-muted mt-1">{{ card.sub }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Progress -->
      <div class="lg:col-span-2 glass-panel p-5">
        <h3 class="text-sm font-semibold text-cockpit-gold mb-4">项目执行进度</h3>
        <div v-if="progress.length" class="space-y-3">
          <div v-for="p in progress" :key="p.project_id" class="flex items-center gap-3">
            <span class="text-sm w-24 truncate">{{ p.project_name }}</span>
            <div class="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all duration-500"
                :class="p.completion_rate >= 80 ? 'bg-green-500' : p.completion_rate >= 50 ? 'bg-cockpit-gold' : 'bg-cockpit-accent'"
                :style="{ width: p.completion_rate + '%' }" />
            </div>
            <span class="text-xs text-cockpit-muted w-12 text-right">{{ p.completion_rate }}%</span>
            <span class="text-xs text-cockpit-muted">{{ p.completed_tasks }}/{{ p.total_tasks }}</span>
          </div>
        </div>
        <p v-else class="text-cockpit-muted text-sm py-4 text-center">暂无项目数据，请先创建项目和计划</p>
      </div>

      <!-- Risk alerts -->
      <div class="glass-panel p-5">
        <h3 class="text-sm font-semibold text-cockpit-accent mb-4">⚠ 风险预警</h3>
        <div v-if="risks.length" class="space-y-2">
          <div v-for="r in risks.slice(0, 5)" :key="r.id"
            class="p-2.5 rounded-lg bg-cockpit-accent/5 border border-cockpit-accent/20 text-sm">
            <span class="text-cockpit-accent font-medium">{{ r.type === 'severe_defect' ? '严重缺陷' : '延期任务' }}: </span>
            <span class="text-cockpit-text">{{ r.title }}</span>
          </div>
        </div>
        <p v-else class="text-cockpit-muted text-sm py-4 text-center">当前无风险预警 ✓</p>
      </div>
    </div>

    <!-- My Todos -->
    <div class="glass-panel p-5">
      <h3 class="text-sm font-semibold text-cockpit-gold mb-4">我的待办</h3>
      <div v-if="todos.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        <div v-for="t in todos.slice(0, 9)" :key="t.id"
          class="p-3 rounded-lg bg-white/3 border border-cockpit-border/20 flex justify-between items-center">
          <div>
            <span class="text-xs px-1.5 py-0.5 rounded mr-2"
              :class="t.type === 'task' ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'">
              {{ t.type === 'task' ? '任务' : '缺陷' }}
            </span>
            <span class="text-sm">{{ t.title }}</span>
          </div>
          <span class="badge"
            :class="t.priority === 'urgent' ? 'badge-urgent' : t.priority === 'high' ? 'badge-high' : 'badge-todo'">
            {{ t.priority }}
          </span>
        </div>
      </div>
      <p v-else class="text-cockpit-muted text-sm py-4 text-center">暂无待办事项 ✓</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api/client'

const kpiCards = ref([
  { label: '项目总数', value: 0, sub: '', link: '/plans' },
  { label: '进行中项目', value: 0, sub: '', link: '/plans' },
  { label: '任务完成率', value: '0%', sub: '', link: '/dashboard' },
  { label: '延期任务', value: 0, sub: '', link: '/plans' },
  { label: '待评审需求', value: 0, sub: '', link: '/requirements' },
  { label: '未关闭缺陷', value: 0, sub: '', link: '/defects' },
])

const progress = ref<any[]>([])
const risks = ref<any[]>([])
const todos = ref<any[]>([])

onMounted(async () => {
  try {
    const [summary, prog, risk, todo] = await Promise.all([
      api.get('/dashboard/summary'),
      api.get('/dashboard/progress'),
      api.get('/dashboard/risks'),
      api.get('/dashboard/my-todos'),
    ])
    const s: any = summary.data
    kpiCards.value = [
      { label: '项目总数', value: s.total_projects, sub: '', link: '/plans' },
      { label: '进行中项目', value: s.active_projects, sub: '', link: '/plans' },
      { label: '任务完成率', value: s.task_completion_rate + '%', sub: '', link: '/dashboard' },
      { label: '延期任务', value: s.overdue_tasks, sub: '', link: '/plans' },
      { label: '待评审需求', value: s.pending_requirements, sub: '', link: '/requirements' },
      { label: '未关闭缺陷', value: s.open_defects, sub: '', link: '/defects' },
    ]
    progress.value = (prog as any).data || []
    risks.value = (risk as any).data || []
    todos.value = (todo as any).data || []
  } catch { /* ignore */ }
})
</script>
