<template>
  <div class="space-y-4">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-glow">甘特图</h2>
      <div class="flex gap-2 items-center">
        <select v-model="selectedPlanId" @change="loadGantt" class="px-3 py-1.5 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm">
          <option :value="0">选择计划...</option>
          <option v-for="p in plans" :key="p.id" :value="p.id">{{ p.name }}</option>
        </select>
        <div class="flex rounded-lg overflow-hidden border border-cockpit-border/30">
          <button v-for="mode in ['day','week','month']" :key="mode" @click="viewMode=mode"
            class="px-3 py-1.5 text-xs transition-colors"
            :class="viewMode===mode?'bg-cockpit-accent text-white':'bg-white/5 text-cockpit-muted hover:text-cockpit-text'">
            {{ mode==='day'?'日':mode==='week'?'周':'月' }}
          </button>
        </div>
      </div>
    </div>
    <div v-if="!selectedPlanId" class="glass-panel p-8 text-center text-cockpit-muted">请先选择一个计划查看甘特图</div>
    <div v-else class="glass-panel overflow-x-auto">
      <div ref="canvasContainer" class="relative" style="min-width:800px">
        <canvas ref="canvas" class="w-full" :height="canvasHeight"></canvas>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import api from '@/api/client'

const plans = ref<any[]>([])
const selectedPlanId = ref(0)
const viewMode = ref('day')
const canvas = ref<HTMLCanvasElement>()
const canvasHeight = ref(600)
const ganttData = ref<any>({ tasks: [], milestones: [], dependencies: [] })

onMounted(async () => {
  try { const r: any = await api.get('/plans'); plans.value = r.data?.items || [] } catch {}
})

async function loadGantt() {
  if (!selectedPlanId.value) return
  try { const r: any = await api.get(`/tasks/gantt/${selectedPlanId.value}`); ganttData.value = r.data; await nextTick(); drawGantt() } catch {}
}

watch(viewMode, () => { if (selectedPlanId.value) drawGantt() })

function drawGantt() {
  const c = canvas.value; if (!c) return
  const ctx = c.getContext('2d'); if (!ctx) return
  const tasks = ganttData.value.tasks || []
  const milestones = ganttData.value.milestones || []

  const dpr = window.devicePixelRatio || 1
  const width = Math.max(900, (c.parentElement?.clientWidth || 900))
  canvasHeight.value = Math.max(400, tasks.length * 44 + 120)
  c.width = width * dpr; c.height = canvasHeight.value * dpr
  c.style.width = width + 'px'; c.style.height = canvasHeight.value + 'px'
  ctx.scale(dpr, dpr)

  // Calculate date range
  const now = new Date()
  let minDate = new Date(now.getFullYear(), now.getMonth() - 1, 1)
  let maxDate = new Date(now.getFullYear(), now.getMonth() + 3, 1)
  tasks.forEach((t: any) => {
    if (t.start_date) { const d = new Date(t.start_date); if (d < minDate) minDate = d }
    if (t.end_date) { const d = new Date(t.end_date); if (d > maxDate) maxDate = d }
  })

  const leftMargin = 220, topMargin = 40, rightMargin = 20
  const chartWidth = width - leftMargin - rightMargin
  const totalDays = Math.ceil((maxDate.getTime() - minDate.getTime()) / 86400000) + 1
  const dayWidth = chartWidth / totalDays

  // Background
  ctx.fillStyle = '#0A0E17'; ctx.fillRect(0, 0, width, canvasHeight.value)

  // Grid lines
  ctx.strokeStyle = 'rgba(255,255,255,0.04)'; ctx.lineWidth = 1
  const gridInterval = viewMode.value === 'day' ? 7 : viewMode.value === 'week' ? 14 : 30
  for (let d = 0; d <= totalDays; d += gridInterval) {
    const x = leftMargin + d * dayWidth
    ctx.beginPath(); ctx.moveTo(x, topMargin); ctx.lineTo(x, canvasHeight.value - 20); ctx.stroke()
  }

  // Today line
  const todayOffset = Math.ceil((now.getTime() - minDate.getTime()) / 86400000)
  const todayX = leftMargin + todayOffset * dayWidth
  ctx.strokeStyle = '#FF4D2E'; ctx.lineWidth = 2
  ctx.beginPath(); ctx.moveTo(todayX, topMargin); ctx.lineTo(todayX, canvasHeight.value - 20); ctx.stroke()
  ctx.fillStyle = '#FF4D2E'; ctx.font = '11px Inter'; ctx.fillText('今天', todayX + 4, topMargin + 14)

  // Date header
  ctx.fillStyle = '#94A3B8'; ctx.font = '11px Inter'
  for (let d = 0; d <= totalDays; d += gridInterval) {
    const date = new Date(minDate.getTime() + d * 86400000)
    const x = leftMargin + d * dayWidth
    const label = viewMode.value === 'month' ? `${date.getMonth()+1}月` : `${date.getMonth()+1}/${date.getDate()}`
    ctx.fillText(label, x + 2, topMargin - 8)
  }

  // Tasks
  tasks.forEach((t: any, i: number) => {
    const y = topMargin + 30 + i * 44
    // Task label
    ctx.fillStyle = '#F5F5F5'; ctx.font = '12px Inter'; ctx.fillText(t.title || `Task #${t.id}`, 10, y + 18)
    ctx.fillStyle = '#94A3B8'; ctx.font = '10px Inter'
    const statusLabel = { todo: '待办', in_progress: '进行中', done: '完成', blocked: '阻塞', review: '审核中' }[t.status] || t.status
    ctx.fillText(statusLabel, 10, y + 34)

    // Task bar
    const startD = t.start_date ? new Date(t.start_date) : new Date()
    const endD = t.end_date ? new Date(t.end_date) : new Date(startD.getTime() + 7*86400000)
    const sx = leftMargin + Math.ceil((startD.getTime() - minDate.getTime()) / 86400000) * dayWidth
    const barW = Math.max(4, Math.ceil((endD.getTime() - startD.getTime()) / 86400000) * dayWidth + dayWidth)
    const barH = 20

    const colors: Record<string, string> = { done: '#22C55E', in_progress: '#3B82F6', blocked: '#FF4D2E', review: '#F59E0B', todo: '#64748B' }
    ctx.fillStyle = colors[t.status] || '#64748B'
    ctx.globalAlpha = 0.85; ctx.fillRect(sx, y + 8, barW > 0 ? barW : 4, barH); ctx.globalAlpha = 1
    ctx.fillStyle = '#0A0E17'; ctx.font = '9px Inter'
    if (barW > 30) ctx.fillText(t.title || '', sx + 4, y + 22)
  })

  // Milestones
  milestones.forEach((m: any) => {
    if (!m.date) return
    const mDate = new Date(m.date)
    const mx = leftMargin + Math.ceil((mDate.getTime() - minDate.getTime()) / 86400000) * dayWidth
    const my = topMargin + 5
    ctx.fillStyle = '#FFB347'
    ctx.beginPath(); ctx.moveTo(mx, my); ctx.lineTo(mx + 8, my + 14); ctx.lineTo(mx, my + 28); ctx.lineTo(mx - 8, my + 14); ctx.closePath()
    ctx.fill()
    ctx.fillStyle = '#FFB347'; ctx.font = '10px Inter'; ctx.fillText(m.title, mx - ctx.measureText(m.title).width/2, my - 6)
  })
}
</script>
