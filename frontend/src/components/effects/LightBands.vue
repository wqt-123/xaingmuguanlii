<template>
  <div class="fixed inset-0 pointer-events-none overflow-hidden" style="z-index:0">
    <!-- Top light band -->
    <div class="absolute top-0 left-0 right-0 h-[2px]"
      style="background: linear-gradient(90deg, transparent 0%, rgba(255,77,46,0.6) 20%, rgba(255,179,71,0.8) 50%, rgba(255,77,46,0.6) 80%, transparent 100%);
             animation: lightBandFlow 8s linear infinite; box-shadow: 0 0 20px rgba(255,77,46,0.3), 0 0 40px rgba(255,179,71,0.15)" />
    <!-- Bottom light band -->
    <div class="absolute bottom-0 left-0 right-0 h-[2px]"
      style="background: linear-gradient(90deg, transparent 0%, rgba(255,179,71,0.6) 20%, rgba(255,77,46,0.8) 50%, rgba(255,179,71,0.6) 80%, transparent 100%);
             animation: lightBandFlow 8s linear infinite reverse; box-shadow: 0 0 20px rgba(255,179,71,0.3), 0 0 40px rgba(255,77,46,0.15)" />
    <!-- Ambient glow spots -->
    <div class="absolute top-[15%] left-[10%] w-96 h-96 rounded-full blur-[120px]"
      style="background: rgba(255,77,46,0.04); animation: ambientGlow 6s ease-in-out infinite" />
    <div class="absolute bottom-[20%] right-[5%] w-80 h-80 rounded-full blur-[100px]"
      style="background: rgba(255,179,71,0.04); animation: ambientGlow 7s ease-in-out infinite 2s" />
  </div>
</template>

<style scoped>
@keyframes lightBandFlow {
  0% { transform: translateX(-100%); opacity: 0.4; }
  50% { opacity: 1; }
  100% { transform: translateX(100%); opacity: 0.4; }
}
@keyframes ambientGlow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.3); opacity: 1; }
}
</style>
