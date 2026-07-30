<template>
  <div class="relative" :style="{height:height+'px'}">
    <canvas ref="canvas" class="w-full h-full" />
    <div class="absolute bottom-2 left-2 text-[10px] text-cockpit-muted flex gap-3">
      <span v-for="l in labels" :key="l">{{ l }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'

const props = withDefaults(defineProps<{
  data: number[]; labels?: string[]; height?: number; color?: string
}>(), { data: () => [0], labels: () => [], height: 200, color: '#FFB347' })

const canvas = ref<HTMLCanvasElement>()
let animId = 0; let drawProgress = 0

function draw() {
  const c = canvas.value; if (!c) return
  const ctx = c.getContext('2d'); if (!ctx) return
  const dpr = window.devicePixelRatio || 1
  const w = c.parentElement?.clientWidth || 600
  const h = props.height
  c.width = w * dpr; c.height = h * dpr
  c.style.width = w + 'px'; c.style.height = h + 'px'
  ctx.scale(dpr, dpr)

  const data = props.data; const len = data.length
  if (len < 2) return
  const maxVal = Math.max(...data, 1); const minVal = Math.min(...data, 0)
  const range = maxVal - minVal || 1
  const pad = 30; const chartW = w - pad * 2; const chartH = h - pad * 2

  // Grid
  ctx.strokeStyle = 'rgba(255,255,255,0.04)'; ctx.lineWidth = 1
  for (let i = 0; i <= 4; i++) {
    const y = pad + (chartH / 4) * i
    ctx.beginPath(); ctx.moveTo(pad, y); ctx.lineTo(w - pad, y); ctx.stroke()
  }

  // Draw line with flowing light effect
  const progress = Math.min(1, drawProgress)
  const pointsToDraw = Math.ceil(len * progress)

  // Gradient fill under line
  const fillGrad = ctx.createLinearGradient(0, pad, 0, h - pad)
  fillGrad.addColorStop(0, `${props.color}22`)
  fillGrad.addColorStop(1, `${props.color}00`)
  ctx.beginPath()
  ctx.moveTo(pad, h - pad)
  for (let i = 0; i < pointsToDraw; i++) {
    const x = pad + (chartW / (len - 1)) * i
    const y = pad + chartH - ((data[i] - minVal) / range) * chartH
    ctx.lineTo(x, y)
  }
  ctx.lineTo(pad + (chartW / (len - 1)) * (pointsToDraw - 1), h - pad)
  ctx.closePath(); ctx.fill()

  // Main line with glow
  ctx.strokeStyle = props.color; ctx.lineWidth = 2.5
  ctx.shadowColor = props.color; ctx.shadowBlur = 8
  ctx.beginPath()
  for (let i = 0; i < pointsToDraw; i++) {
    const x = pad + (chartW / (len - 1)) * i
    const y = pad + chartH - ((data[i] - minVal) / range) * chartH
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
  }
  ctx.stroke(); ctx.shadowBlur = 0

  // End point dot
  if (pointsToDraw > 0) {
    const lastX = pad + (chartW / (len - 1)) * (pointsToDraw - 1)
    const lastY = pad + chartH - ((data[pointsToDraw - 1] - minVal) / range) * chartH
    ctx.fillStyle = props.color; ctx.shadowColor = props.color; ctx.shadowBlur = 12
    ctx.beginPath(); ctx.arc(lastX, lastY, 4, 0, Math.PI * 2); ctx.fill()
    ctx.shadowBlur = 0
  }
}

function animate() {
  drawProgress += 0.04
  draw()
  if (drawProgress < 1) animId = requestAnimationFrame(animate)
}

onMounted(() => { drawProgress = 0; animate() })
watch(() => props.data, () => { drawProgress = 0; animate() })
onUnmounted(() => cancelAnimationFrame(animId))
</script>
