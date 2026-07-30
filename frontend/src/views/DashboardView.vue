<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-bold text-glow">作战总览</h2>
    <!-- KPI Cards with animated numbers -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      <div v-for="(card,i) in kpiCards" :key="card.label"
        class="glass-panel p-4 text-center cursor-pointer hover:scale-[1.03] transition-all"
        :class="i % 2 === 0 ? 'glass-panel-left' : 'glass-panel-right'"
        :style="`animation-delay:${i * 0.1}s`"
        @click="$router.push(card.link)">
        <p class="text-[11px] text-cockpit-muted mb-1.5 uppercase tracking-wider">{{ card.label }}</p>
        <p class="text-2xl font-bold data-value-glow" style="font-family:'JetBrains Mono',monospace"
          :class="card.alert ? 'text-cockpit-accent alert-pulse' : ''">
          {{ animatedValues[i] }}{{ card.suffix }}
        </p>
        <p v-if="card.sub" class="text-[10px] text-cockpit-muted mt-1">{{ card.sub }}</p>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <!-- Progress Ring -->
      <div class="glass-panel p-5 flex flex-col items-center">
        <h3 class="text-sm font-semibold text-cockpit-gold mb-3">任务完成率</h3>
        <DonutRing :percent="completionRate" label="完成任务" :size="140" />
      </div>

      <!-- Trend Line -->
      <div class="lg:col-span-2 glass-panel p-5">
        <h3 class="text-sm font-semibold text-cockpit-gold mb-3">执行趋势 (最近7天)</h3>
        <TrendLine :data="trendData" :labels="['周一','周二','周三','周四','周五','周六','周日']" :height="180" />
      </div>
    </div>

    <!-- Progress + Risk Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <!-- Project progress bars -->
      <div class="glass-panel p-5">
        <h3 class="text-sm font-semibold text-cockpit-gold mb-4">项目执行进度</h3>
        <div v-if="progress.length" class="space-y-3">
          <div v-for="p in progress" :key="p.project_id" class="group">
            <div class="flex justify-between text-xs mb-1">
              <span class="truncate max-w-[140px]">{{ p.project_name }}</span>
              <span class="data-value-glow" :class="colorForRate(p.completion_rate)">
                {{ p.completion_rate }}%
              </span>
            </div>
            <div class="h-2 bg-white/5 rounded-full overflow-hidden relative">
              <div class="h-full rounded-full transition-all duration-700 ease-out relative"
                :style="{ width: p.completion_rate + '%', background: barGradient(p.completion_rate) }">
                <!-- Shimmer effect on active bars -->
                <div v-if="p.completion_rate > 0 && p.completion_rate < 100"
                  class="absolute inset-0 rounded-full"
                  style="background: linear-gradient(90deg,transparent 0%,rgba(255,255,255,0.3) 50%,transparent 100%); background-size:200% 100%; animation: shimmer 2s infinite" />
              </div>
            </div>
          </div>
        </div>
        <p v-else class="text-cockpit-muted text-xs py-6 text-center">暂无项目数据</p>
      </div>

      <!-- Risk Alerts -->
      <div class="glass-panel p-5">
        <h3 class="text-sm font-semibold text-cockpit-accent mb-4 flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-cockpit-accent alert-pulse" />
          ⚠ 风险预警
        </h3>
        <div v-if="risks.length" class="space-y-2">
          <div v-for="(r,i) in risks.slice(0,6)" :key="r.id"
            class="p-3 rounded-lg border transition-all hover:bg-cockpit-accent/5"
            :class="r.type==='severe_defect'?'border-cockpit-accent/30 alert-pulse-border':'border-cockpit-border/15'"
            :style="`animation-delay:${i*0.1}s`">
            <div class="flex items-center gap-2">
              <span class="text-xs px-1.5 py-0.5 rounded"
                :class="r.type==='severe_defect'?'badge-urgent':'badge-high'">
                {{ r.type === 'severe_defect' ? '严重缺陷' : '延期' }}
              </span>
              <span class="text-sm truncate flex-1">{{ r.title }}</span>
            </div>
            <p v-if="r.due_date" class="text-[10px] text-cockpit-muted mt-1 ml-1">
              截止: {{ r.due_date?.split('T')[0] }}
            </p>
          </div>
        </div>
        <p v-else class="text-cockpit-muted text-xs py-6 text-center">✓ 当前无风险预警</p>
      </div>
    </div>

    <!-- My Todos -->
    <div class="glass-panel p-5">
      <h3 class="text-sm font-semibold text-cockpit-gold mb-4">我的待办</h3>
      <div v-if="todos.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        <div v-for="t in todos.slice(0,9)" :key="t.id"
          class="p-3 rounded-lg border border-cockpit-border/15 hover:border-cockpit-gold/30 transition-all flex justify-between items-center"
          :class="t.priority==='urgent'||t.priority==='high'?'bg-cockpit-accent/5':''">
          <div class="flex items-center gap-2 min-w-0">
            <span class="w-1.5 h-1.5 rounded-full flex-shrink-0"
              :class="t.type==='defect'?'bg-cockpit-accent':'bg-cockpit-gold'" />
            <span class="text-xs px-1.5 py-0.5 rounded flex-shrink-0"
              :class="t.type==='defect'?'bg-red-500/15 text-red-400':'bg-blue-500/15 text-blue-400'">
              {{ t.type === 'task' ? '任务' : '缺陷' }}
            </span>
            <span class="text-sm truncate">{{ t.title }}</span>
          </div>
          <span class="text-[10px] px-1.5 py-0.5 rounded ml-2 flex-shrink-0"
            :class="priorityBadge(t.priority)">
            {{ t.priority }}
          </span>
        </div>
      </div>
      <p v-else class="text-cockpit-muted text-xs py-6 text-center">暂无待办 ✓</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import api from '@/api/client'
import DonutRing from '@/components/dashboard/DonutRing.vue'
import TrendLine from '@/components/dashboard/TrendLine.vue'

const completionRate = ref(0)
const progress = ref<any[]>([])
const risks = ref<any[]>([])
const todos = ref<any[]>([])
const trendData = ref<number[]>([0,0,0,0,0,0,0])

// Animated KPI values
const targetValues = ref([0,0,0,0,0,0])
const animatedValues = ref([0,0,0,0,0,0])
let animTimer = 0

const kpiCards = ref([
  { label: '项目总数', suffix: '', link: '/projects', alert: false, sub: '' },
  { label: '进行中', suffix: '', link: '/projects', alert: false, sub: '' },
  { label: '完成率', suffix: '%', link: '/dashboard', alert: false, sub: '' },
  { label: '延期任务', suffix: '', link: '/projects', alert: true, sub: '' },
  { label: '待评审', suffix: '', link: '/requirements', alert: false, sub: '' },
  { label: '未关闭缺陷', suffix: '', link: '/defects', alert: true, sub: '' },
])

const colorForRate = (r: number) => r >= 80 ? 'text-green-400' : r >= 50 ? 'text-cockpit-gold' : 'text-cockpit-accent'
const barGradient = (r: number) => r >= 80 ? 'linear-gradient(90deg,#22C55E,#4ADE80)' : r >= 50 ? 'linear-gradient(90deg,#FFB347,#FBBF24)' : 'linear-gradient(90deg,#FF4D2E,#F97316)'
const priorityBadge = (p: string) => p === 'urgent' ? 'badge-urgent' : p === 'high' ? 'badge-high' : 'badge-todo'

function animateNumbers() {
  let changed = false
  for (let i = 0; i < targetValues.value.length; i++) {
    const target = targetValues.value[i]
    const current = animatedValues.value[i]
    if (Math.abs(current - target) < 1) {
      animatedValues.value[i] = target
    } else {
      animatedValues.value[i] = Math.round(current + (target - current) * 0.3)
      changed = true
    }
  }
  if (changed) animTimer = requestAnimationFrame(animateNumbers)
}

onMounted(async () => {
  try {
    const [summary, prog, risk, todo]: any[] = await Promise.all([
      api.get('/dashboard/summary'),
      api.get('/dashboard/progress'),
      api.get('/dashboard/risks'),
      api.get('/dashboard/my-todos'),
    ])
    const s = summary.data
    targetValues.value = [s.total_projects, s.active_projects, s.task_completion_rate, s.overdue_tasks, s.pending_requirements, s.open_defects]
    animatedValues.value = [0,0,0,0,0,0]
    animTimer = requestAnimationFrame(animateNumbers)
    completionRate.value = s.task_completion_rate
    kpiCards.value[0].value = s.total_projects
    kpiCards.value[4].value = s.pending_requirements
    progress.value = (prog as any).data || []
    risks.value = (risk as any).data || []
    todos.value = (todo as any).data || []
    // Generate trend data from progress
    if (progress.value.length > 0) {
      trendData.value = progress.value.map((p: any) => p.completion_rate || 0)
      if (trendData.value.length < 2) trendData.value = [20,35,50,45,60,70,completionRate.value]
    }
  } catch {}
})

onUnmounted(() => cancelAnimationFrame(animTimer))
</script>
