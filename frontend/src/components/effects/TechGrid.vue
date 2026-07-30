<template>
  <div class="fixed bottom-0 left-0 right-0 pointer-events-none" style="z-index:0; perspective:800px">
    <svg class="w-full" viewBox="0 0 1200 300" preserveAspectRatio="none" style="height:200px">
      <defs>
        <linearGradient id="gridGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="rgba(255,107,53,0.15)" />
          <stop offset="100%" stop-color="rgba(255,107,53,0)" />
        </linearGradient>
      </defs>
      <!-- Horizontal lines (perspective grid) -->
      <g v-for="i in 12" :key="'h'+i"
        :transform="`translate(0,${15 + i * 20})`"
        :style="`opacity:${0.04 + i * 0.02}`">
        <line :x1="600 - i * 55" :y1="0" :x2="600 + i * 55" :y2="0"
          stroke="rgba(255,107,53,0.5)" stroke-width="1" />
        <!-- Nodes on grid -->
        <circle v-for="j in (i * 2 + 1)" :key="'n'+i+'-'+j"
          :cx="600 + (j - i - 1) * (55 / (i * 0.2 + 0.5))"
          :cy="0" r="1.5" fill="rgba(255,179,71,0.3)"
          class="grid-node" />
      </g>
    </svg>
  </div>
</template>

<style scoped>
.grid-node {
  animation: nodePulse 4s ease-in-out infinite;
  animation-delay: calc(var(--i, 0) * 0.2s);
}
@keyframes nodePulse {
  0%, 100% { opacity: 0.2; r: 1.5px; }
  50% { opacity: 0.8; r: 3px; fill: #FFB347; filter: drop-shadow(0 0 4px #FFB347); }
}
</style>
