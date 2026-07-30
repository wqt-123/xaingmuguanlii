<template>
  <div class="flex h-screen bg-cockpit-bg relative">
    <!-- PRD 6.1.4 Background Effects Layer -->
    <ParticleBackground />
    <LightBands />
    <TechGrid />
    <!-- Main UI Layer (above effects) -->
    <div class="flex w-full relative" style="z-index:1">
      <Sidebar />
      <div class="flex-1 flex flex-col overflow-hidden">
        <Topbar />
        <main class="flex-1 overflow-auto p-6">
          <router-view v-slot="{ Component }">
            <transition name="page" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Sidebar from './Sidebar.vue'
import Topbar from './Topbar.vue'
import ParticleBackground from '@/components/effects/ParticleBackground.vue'
import LightBands from '@/components/effects/LightBands.vue'
import TechGrid from '@/components/effects/TechGrid.vue'
</script>

<style scoped>
/* PRD 6.2.2: Page transition animation */
.page-enter-active {
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}
.page-leave-active {
  transition: all 0.15s ease-in;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px) scale(0.995);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
