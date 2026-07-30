<template>
  <canvas ref="canvas" class="fixed inset-0 pointer-events-none" style="z-index:0" />
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const canvas = ref<HTMLCanvasElement>()
let animId = 0

class Particle {
  x: number = 0; y: number = 0; vx: number = 0; vy: number = 0
  size: number = 1; alpha: number = 0; pulseSpeed: number = 0; pulseOffset: number = 0

  constructor(w: number, h: number) {
    this.reset(w, h)
  }
  reset(w: number, h: number) {
    this.x = Math.random() * w
    this.y = Math.random() * h
    this.vx = (Math.random() - 0.5) * 0.5
    this.vy = (Math.random() - 0.5) * 0.5
    this.size = Math.random() * 2 + 0.5
    this.alpha = Math.random() * 0.6 + 0.2
    this.pulseSpeed = Math.random() * 0.02 + 0.005
    this.pulseOffset = Math.random() * Math.PI * 2
  }
  update(w: number, h: number, t: number) {
    this.x += this.vx
    this.y += this.vy
    if (this.x < 0) this.x = w
    if (this.x > w) this.x = 0
    if (this.y < 0) this.y = h
    if (this.y > h) this.y = 0
    this.alpha = 0.2 + Math.sin(t * this.pulseSpeed + this.pulseOffset) * 0.3 + 0.3
  }
}

onMounted(() => {
  const c = canvas.value; if (!c) return
  const ctx = c.getContext('2d'); if (!ctx) return

  const resize = () => {
    c.width = window.innerWidth; c.height = window.innerHeight
  }
  resize(); window.addEventListener('resize', resize)

  const particles: Particle[] = []
  const count = 80
  for (let i = 0; i < count; i++) particles.push(new Particle(c.width, c.height))

  let t = 0
  function animate() {
    t++; ctx!.clearRect(0, 0, c!.width, c!.height)

    // Draw connections between nearby particles
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x
        const dy = particles[i].y - particles[j].y
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist < 120) {
          ctx!.beginPath()
          ctx!.strokeStyle = `rgba(255,179,71,${0.08 * (1 - dist / 120)})`
          ctx!.lineWidth = 0.5
          ctx!.moveTo(particles[i].x, particles[i].y)
          ctx!.lineTo(particles[j].x, particles[j].y)
          ctx!.stroke()
        }
      }
    }

    for (const p of particles) {
      p.update(c!.width, c!.height, t)
      // Glow effect on each particle
      const grad = ctx!.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size * 4)
      grad.addColorStop(0, `rgba(255,179,71,${p.alpha})`)
      grad.addColorStop(0.5, `rgba(255,179,71,${p.alpha * 0.3})`)
      grad.addColorStop(1, 'rgba(255,179,71,0)')
      ctx!.fillStyle = grad
      ctx!.beginPath()
      ctx!.arc(p.x, p.y, p.size * 4, 0, Math.PI * 2)
      ctx!.fill()

      // Core dot
      ctx!.fillStyle = `rgba(255,179,71,${p.alpha})`
      ctx!.beginPath()
      ctx!.arc(p.x, p.y, p.size, 0, Math.PI * 2)
      ctx!.fill()
    }

    animId = requestAnimationFrame(animate)
  }
  animate()
})

onUnmounted(() => cancelAnimationFrame(animId))
</script>
