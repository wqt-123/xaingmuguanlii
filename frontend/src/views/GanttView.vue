<template>
  <div class="space-y-3">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-glow">甘特图</h2>
      <div class="flex gap-2 items-center">
        <select v-model="selectedPlanId" @change="loadGantt" class="px-3 py-1.5 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm">
          <option :value="0">选择项目...</option>
          <option v-for="p in plans" :key="p.id" :value="p.id">{{ p.name }}</option>
        </select>
        <div class="flex rounded-lg overflow-hidden border border-cockpit-border/30">
          <button v-for="mode in ['day','week','month']" :key="mode" @click="viewMode=mode;drawGantt()"
            class="px-3 py-1.5 text-xs transition-colors"
            :class="viewMode===mode?'bg-cockpit-accent text-white':'bg-white/5 text-cockpit-muted hover:text-cockpit-text'">
            {{ mode==='day'?'日':mode==='week'?'周':'月' }}
          </button>
        </div>
      </div>
    </div>
    <div v-if="!selectedPlanId" class="glass-panel p-8 text-center text-cockpit-muted">请先选择一个项目查看甘特图</div>
    <div v-else class="glass-panel overflow-hidden relative">
      <div class="text-xs text-cockpit-muted p-2 border-b border-cockpit-border/20">
        💡 拖拽任务条移动日期 | 拖拽边缘调整工期 | 右键任务条添加依赖 | 拖拽里程碑
      </div>
      <div ref="canvasWrap" class="overflow-x-auto" @contextmenu.prevent>
        <canvas ref="canvas" :height="canvasHeight" class="cursor-pointer" style="min-width:900px"
          @mousedown="onMouseDown" @mousemove="onMouseMove" @mouseup="onMouseUp" @mouseleave="onMouseUp"
          @contextmenu="onContextMenu" />
      </div>
      <!-- Context Menu -->
      <div v-if="ctxMenu.show" class="fixed glass-panel p-1.5 z-50 shadow-2xl border-cockpit-gold/50" :style="{left:ctxMenu.x+'px',top:ctxMenu.y+'px'}">
        <button v-for="a in ctxActions" :key="a.label" @click="a.action"
          class="block w-full text-left px-3 py-1.5 text-xs rounded hover:bg-white/10 transition-colors"
          :class="a.danger ? 'text-cockpit-accent' : 'text-cockpit-text'">{{ a.label }}</button>
      </div>
      <div v-if="linkMode" class="fixed top-4 left-1/2 -translate-x-1/2 z-50 glass-panel px-4 py-2 text-sm animate-slide-up border-cockpit-gold/50">
        点击目标任务完成连线 ({{ linkMode }}) <button @click="linkMode=''" class="ml-2 text-cockpit-accent">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import api from '@/api/client'

const canvas = ref<HTMLCanvasElement>()
const canvasWrap = ref<HTMLDivElement>()
const plans = ref<any[]>([])
const selectedPlanId = ref(0)
const viewMode = ref('day')
const canvasHeight = ref(600)
const ganttData = ref<any>({ tasks: [], milestones: [], dependencies: [] })
const linkMode = ref('')
const linkFromId = ref(0)
const ctxMenu = ref({ show: false, x: 0, y: 0, taskId: 0 })
const ctxActions = ref<any[]>([])

// Drag state
let dragMode = ''  // 'move' | 'resize-left' | 'resize-right' | 'milestone'
let dragTask: any = null
let dragStartX = 0; let dragOrigStart = 0; let dragOrigEnd = 0
let minDate = new Date(); let maxDate = new Date(); let chartW = 800; let dayW = 1
let leftM = 220; let topM = 60
let taskRects: { id: number; x: number; y: number; w: number; h: number; isMilestone?: boolean }[] = []

onMounted(async () => {
  try { const r: any = await api.get('/plans'); plans.value = r.data?.items || [] } catch {}
})

async function loadGantt() {
  if (!selectedPlanId.value) return
  try {
    const [gr, dr]: any[] = await Promise.all([
      api.get(`/tasks/gantt/${selectedPlanId.value}`),
      api.get(`/tasks/dependencies/${selectedPlanId.value}`)
    ])
    ganttData.value = gr.data
    ganttData.value.dependencies = dr.data || []
    await nextTick(); drawGantt()
  } catch {}
}

const statusColors: Record<string, string> = {
  done: '#22C55E', in_progress: '#3B82F6', pending: '#F59E0B', todo: '#64748B', blocked: '#FF4D2E', review: '#A855F7'
}

function drawGantt() {
  const c = canvas.value; if (!c) return
  const ctx = c.getContext('2d'); if (!ctx) return
  const tasks = ganttData.value.tasks || []
  const milestones = ganttData.value.milestones || []
  const deps = ganttData.value.dependencies || []

  const dpr = window.devicePixelRatio || 1
  const w = Math.max(1000, canvasWrap.value?.clientWidth || 1000)
  canvasHeight.value = Math.max(400, tasks.length * 50 + milestones.length * 30 + 140)
  c.width = w * dpr; c.height = canvasHeight.value * dpr
  c.style.width = w + 'px'; c.style.height = canvasHeight.value + 'px'
  ctx.scale(dpr, dpr)
  ctx.clearRect(0, 0, w, canvasHeight.value)

  // Calculate date range
  const now = new Date(); now.setHours(0, 0, 0, 0)
  minDate = new Date(now.getFullYear(), now.getMonth() - 1, 1)
  maxDate = new Date(now.getFullYear(), now.getMonth() + 3, 1)
  tasks.forEach((t: any) => {
    if (t.start_date) { const d = new Date(t.start_date); if (d < minDate) minDate = d }
    if (t.end_date) { const d = new Date(t.end_date); if (d > maxDate) maxDate = d }
  })
  milestones.forEach((m: any) => {
    if (m.date) { const d = new Date(m.date); if (d < minDate) minDate = d; if (d > maxDate) maxDate = d }
  })

  leftM = 220; topM = 60; const rightM = 20
  chartW = w - leftM - rightM
  const totalDays = Math.ceil((maxDate.getTime() - minDate.getTime()) / 86400000) + 1
  dayW = chartW / totalDays

  // Background
  ctx.fillStyle = '#0A0E17'; ctx.fillRect(0, 0, w, canvasHeight.value)

  // Grid
  const gi = viewMode.value === 'day' ? 7 : viewMode.value === 'week' ? 14 : 30
  ctx.strokeStyle = 'rgba(255,255,255,0.03)'; ctx.lineWidth = 1
  for (let d = 0; d <= totalDays; d += gi) {
    const x = leftM + d * dayW
    ctx.beginPath(); ctx.moveTo(x, topM); ctx.lineTo(x, canvasHeight.value); ctx.stroke()
  }

  // Date header
  ctx.fillStyle = '#94A3B8'; ctx.font = '11px Inter'
  for (let d = 0; d <= totalDays; d += gi) {
    const date = new Date(minDate.getTime() + d * 86400000)
    const x = leftM + d * dayW
    ctx.fillText(`${date.getMonth() + 1}/${date.getDate()}`, x + 3, topM - 8)
  }

  // Today line
  const todayOff = Math.floor((now.getTime() - minDate.getTime()) / 86400000)
  const todayX = leftM + todayOff * dayW
  ctx.strokeStyle = '#FF4D2E'; ctx.lineWidth = 1.5; ctx.setLineDash([4, 4])
  ctx.beginPath(); ctx.moveTo(todayX, topM); ctx.lineTo(todayX, canvasHeight.value - 10); ctx.stroke()
  ctx.setLineDash([])
  ctx.fillStyle = '#FF4D2E'; ctx.font = 'bold 11px Inter'; ctx.fillText('今天', todayX + 4, topM + 14)

  // Draw dependency lines FIRST (behind bars)
  deps.forEach((dep: any) => {
    const pred = tasks.find((t: any) => t.id === dep.predecessor_id)
    const succ = tasks.find((t: any) => t.id === dep.successor_id)
    if (!pred || !succ) return
    const pIdx = tasks.indexOf(pred); const sIdx = tasks.indexOf(succ)
    if (pIdx < 0 || sIdx < 0) return
    const pY = topM + 35 + pIdx * 50 + 10
    const sY = topM + 35 + sIdx * 50 + 10
    const pEndD = pred.end_date ? new Date(pred.end_date) : new Date()
    const pX = leftM + Math.floor((pEndD.getTime() - minDate.getTime()) / 86400000) * dayW
    const sStartD = succ.start_date ? new Date(succ.start_date) : new Date()
    const sX = leftM + Math.floor((sStartD.getTime() - minDate.getTime()) / 86400000) * dayW

    ctx.strokeStyle = dep.dep_type === 'FS' ? '#FFB347' : dep.dep_type === 'SS' ? '#60A5FA' : dep.dep_type === 'FF' ? '#F97316' : '#A78BFA'
    ctx.lineWidth = 1.5
    if (dep.dep_type === 'SS') ctx.setLineDash([4, 4])
    else if (dep.dep_type === 'FF') ctx.setLineDash([8, 3])
    else ctx.setLineDash([])

    const midX = (pX + sX) / 2
    ctx.beginPath(); ctx.moveTo(pX, pY)
    ctx.bezierCurveTo(midX, pY, midX, sY, sX, sY)
    ctx.stroke()
    ctx.setLineDash([])

    // Arrow
    ctx.fillStyle = ctx.strokeStyle
    ctx.beginPath(); ctx.moveTo(sX, sY); ctx.lineTo(sX - 7, sY - 4); ctx.lineTo(sX - 7, sY + 4); ctx.closePath(); ctx.fill()
  })

  // Draw tasks
  taskRects = []
  tasks.forEach((t: any, i: number) => {
    const y = topM + 35 + i * 50
    // Task label
    ctx.fillStyle = '#F5F5F5'; ctx.font = '12px Inter'; ctx.fillText(t.title || `Task #${t.id}`, 10, y + 6)
    ctx.fillStyle = '#94A3B8'; ctx.font = '10px Inter'
    const sl = { todo: '待办', pending: '待处理', in_progress: '进行中', done: '已完成', blocked: '阻塞', review: '审核中' }[t.status] || t.status
    ctx.fillText(`${sl} | ${t.assignee_name || '未分配'}`, 10, y + 22)

    // Bar
    const sD = t.start_date ? new Date(t.start_date) : new Date()
    const eD = t.end_date ? new Date(t.end_date) : new Date(sD.getTime() + 5 * 86400000)
    const sx = leftM + Math.floor((sD.getTime() - minDate.getTime()) / 86400000) * dayW
    const bw = Math.max(4, Math.ceil((eD.getTime() - sD.getTime()) / 86400000) * dayW + dayW)
    const barH = 20

    // Bar shadow
    ctx.shadowColor = statusColors[t.status] || '#64748B'; ctx.shadowBlur = 6
    ctx.fillStyle = statusColors[t.status] || '#64748B'
    roundRect(ctx, sx, y + 8, bw, barH, 4)
    ctx.shadowBlur = 0

    // Progress fill
    if (t.status === 'in_progress') {
      ctx.fillStyle = 'rgba(255,255,255,0.15)'
      roundRect(ctx, sx, y + 8, bw * 0.5, barH, 4)
    }

    // Label on bar
    if (bw > 40) {
      ctx.fillStyle = '#FFF'; ctx.font = '9px Inter'
      ctx.fillText(t.title?.slice(0, bw / 6) || '', sx + 4, y + 22)
    }

    // Resize handles
    ctx.fillStyle = 'rgba(255,255,255,0.4)'
    ctx.fillRect(sx - 2, y + 8, 6, barH)
    ctx.fillRect(sx + bw - 4, y + 8, 6, barH)

    taskRects.push({ id: t.id, x: sx, y: y + 8, w: bw, h: barH })
  })

  // Milestones
  milestones.forEach((m: any, i: number) => {
    if (!m.date) return
    const mDate = new Date(m.date)
    const mx = leftM + Math.floor((mDate.getTime() - minDate.getTime()) / 86400000) * dayW
    const my = topM + 35 + tasks.length * 50 + 15 + i * 28
    const ms = m.status === 'completed'
    ctx.fillStyle = ms ? '#22C55E' : '#FFB347'
    ctx.beginPath(); ctx.moveTo(mx, my); ctx.lineTo(mx + 8, my + 12); ctx.lineTo(mx, my + 24); ctx.lineTo(mx - 8, my + 12); ctx.closePath()
    ctx.fill()
    ctx.fillStyle = '#FFB347'; ctx.font = '10px Inter'; ctx.fillText(m.title, mx + 12, my + 14)
    taskRects.push({ id: m.id, x: mx - 8, y: my, w: 16, h: 24, isMilestone: true })
  })
}

function roundRect(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
  ctx.beginPath(); ctx.moveTo(x + r, y); ctx.lineTo(x + w - r, y)
  ctx.arcTo(x + w, y, x + w, y + r, r); ctx.lineTo(x + w, y + h - r)
  ctx.arcTo(x + w, y + h, x + w - r, y + h, r); ctx.lineTo(x + r, y + h)
  ctx.arcTo(x, y + h, x, y + h - r, r); ctx.lineTo(x, y + r)
  ctx.arcTo(x, y, x + r, y, r); ctx.closePath(); ctx.fill()
}

// Mouse handlers
function hitTest(ex: number, ey: number) {
  const c = canvas.value; if (!c) return null
  const rect = c.getBoundingClientRect()
  const x = ex - rect.left; const y = ey - rect.top
  for (const r of taskRects) {
    if (x >= r.x - 4 && x <= r.x + r.w + 4 && y >= r.y - 2 && y <= r.y + r.h + 2) {
      // Check resize handles
      if (!r.isMilestone && x <= r.x + 6) return { type: 'resize-left', rect: r }
      if (!r.isMilestone && x >= r.x + r.w - 6) return { type: 'resize-right', rect: r }
      return { type: r.isMilestone ? 'milestone' : 'move', rect: r }
    }
  }
  return null
}

function onMouseDown(e: MouseEvent) {
  ctxMenu.value.show = false
  // Link mode: clicking on a target task
  if (linkMode.value) {
    const hit = hitTest(e.clientX, e.clientY)
    if (hit && hit.rect.id !== linkFromId.value) {
      api.post('/tasks/dependencies', null, { params: { predecessor_id: linkFromId.value, successor_id: hit.rect.id, dep_type: linkMode.value } }).then(() => { linkMode.value = ''; loadGantt() }).catch(() => {})
    }
    return
  }
  const hit = hitTest(e.clientX, e.clientY)
  if (!hit) return
  dragMode = hit.type
  dragTask = hit.rect
  dragStartX = e.clientX
  const task = findTaskById(hit.rect.id)
  if (task) {
    dragOrigStart = task.start_date ? new Date(task.start_date).getTime() : Date.now()
    dragOrigEnd = task.end_date ? new Date(task.end_date).getTime() : Date.now() + 5 * 86400000
  }
}

function onMouseMove(e: MouseEvent) {
  if (!dragMode || !dragTask) return
  const dx = e.clientX - dragStartX
  const dayShift = Math.round(dx / dayW)
  if (dayShift === 0) return

  const task = findTaskById(dragTask.id)
  if (!task) return
  const newStart = new Date(dragOrigStart + dayShift * 86400000)
  const newEnd = new Date(dragOrigEnd + dayShift * 86400000)

  if (dragMode === 'move') {
    task.start_date = newStart.toISOString()
    task.end_date = newEnd.toISOString()
  } else if (dragMode === 'resize-right') {
    task.end_date = new Date(dragOrigEnd + dayShift * 86400000).toISOString()
    if (new Date(task.end_date) <= new Date(task.start_date)) task.end_date = new Date(new Date(task.start_date).getTime() + 86400000).toISOString()
  } else if (dragMode === 'resize-left') {
    task.start_date = newStart.toISOString()
    if (new Date(task.start_date) >= new Date(task.end_date)) task.start_date = new Date(new Date(task.end_date).getTime() - 86400000).toISOString()
  }
  drawGantt()
}

async function onMouseUp() {
  if (dragMode && dragTask) {
    const task = findTaskById(dragTask.id)
    if (task) {
      try {
        await api.put(`/tasks/${task.id}`, {
          start_date: task.start_date?.split('T')[0],
          end_date: task.end_date?.split('T')[0]
        })
      } catch {}
    }
  }
  dragMode = ''; dragTask = null
}

function findTaskById(id: number) {
  return ganttData.value.tasks?.find((t: any) => t.id === id)
}

function onContextMenu(e: MouseEvent) {
  const hit = hitTest(e.clientX, e.clientY)
  if (!hit) { ctxMenu.value.show = false; return }
  const taskId = hit.rect.id
  ctxMenu.value = { show: true, x: e.clientX, y: e.clientY, taskId }
  ctxActions.value = [
    { label: '添加依赖 → FS', action: () => { linkMode.value = 'FS'; linkFromId.value = taskId; ctxMenu.value.show = false } },
    { label: '添加依赖 → SS', action: () => { linkMode.value = 'SS'; linkFromId.value = taskId; ctxMenu.value.show = false } },
    { label: '添加依赖 → FF', action: () => { linkMode.value = 'FF'; linkFromId.value = taskId; ctxMenu.value.show = false } },
    { label: '删除任务', danger: true, action: async () => {
      if (confirm('删除此任务？')) { try { await api.delete(`/tasks/${taskId}`); await loadGantt() } catch {} }
      ctxMenu.value.show = false
    }},
  ]
}

// Handle link mode click on target
async function handleLinkClick(e: MouseEvent) {
  if (!linkMode.value) return
  const hit = hitTest(e.clientX, e.clientY)
  if (hit && hit.rect.id !== linkFromId.value) {
    try { await api.post('/tasks/dependencies', null, { params: { predecessor_id: linkFromId.value, successor_id: hit.rect.id, dep_type: linkMode.value } }); linkMode.value = ''; await loadGantt() } catch {}
  }
}


// Click handler override for link mode - handled in the template @mousedown
</script>
