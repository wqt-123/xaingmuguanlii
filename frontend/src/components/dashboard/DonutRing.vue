<template>
  <div class="relative inline-flex items-center justify-center">
    <svg :width="size" :height="size" class="transform -rotate-90">
      <!-- Background track -->
      <circle :cx="size/2" :cy="size/2" :r="radius" fill="none"
        stroke="rgba(255,255,255,0.06)" :stroke-width="strokeWidth" />
      <!-- Progress arc with warm gold gradient -->
      <defs>
        <linearGradient :id="gradientId" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#FF4D2E" />
          <stop offset="50%" stop-color="#FFB347" />
          <stop offset="100%" stop-color="#FFB347" />
        </linearGradient>
        <filter :id="glowId">
          <feGaussianBlur stdDeviation="2" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>
      <circle :cx="size/2" :cy="size/2" :r="radius" fill="none"
        :stroke="`url(#${gradientId})`" :stroke-width="strokeWidth"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="offset"
        stroke-linecap="round"
        :filter="`url(#${glowId})`"
        style="transition: stroke-dashoffset 1.2s cubic-bezier(0.22, 1, 0.36, 1)" />
      <!-- Inner glow dot -->
      <circle :cx="size/2" :cy="size/2" r="3" fill="#FFB347" opacity="0.6"
        :filter="`url(#${glowId})`" class="glow-pulse" />
    </svg>
    <!-- Center text -->
    <div class="absolute inset-0 flex flex-col items-center justify-center">
      <span class="text-2xl font-bold data-value-glow" style="font-family:'JetBrains Mono',monospace">{{ Math.round(percent) }}%</span>
      <span class="text-[10px] text-cockpit-muted mt-0.5">{{ label }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  percent: number; label?: string; size?: number; strokeWidth?: number
}>(), { label: '', size: 120, strokeWidth: 10 })

const id = Math.random().toString(36).slice(2, 8)
const gradientId = `ringGrad-${id}`
const glowId = `ringGlow-${id}`
const radius = computed(() => (props.size - props.strokeWidth) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const offset = computed(() => circumference.value * (1 - props.percent / 100))
</script>
