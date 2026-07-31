<template>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden">
    <!-- Background image -->
    <div class="absolute inset-0 z-0">
      <img src="/qingtian/images/login-bg.webp" alt=""
        class="w-full h-full object-cover" />
      <!-- Dark overlay for readability -->
      <div class="absolute inset-0 bg-gradient-to-br from-black/75 via-black/60 to-black/70" />
      <!-- Warm accent overlay -->
      <div class="absolute inset-0" style="background: radial-gradient(ellipse at center, rgba(255,179,71,0.06) 0%, transparent 70%)" />
    </div>

    <!-- Login Card -->
    <div class="relative z-10 w-full max-w-md mx-4 animate-slide-up">
      <div class="backdrop-blur-xl rounded-2xl p-8 text-center"
        style="background: rgba(17,24,39,0.7); border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 8px 40px rgba(0,0,0,0.5);">
        <!-- Logo / Brand -->
        <h1 class="text-2xl font-bold text-white mb-1 tracking-wider drop-shadow-lg">深入云境-Nick</h1>
        <p class="text-xs text-gray-400 mb-8">项目管理作战驾驶舱</p>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <input v-model="username" type="text" placeholder="请输入用户名" autocomplete="username"
              class="w-full px-4 py-3.5 bg-white/8 border border-white/15 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-amber-400/60 focus:ring-1 focus:ring-amber-400/30 transition-all text-sm" />
          </div>
          <div>
            <input v-model="password" type="password" placeholder="请输入密码" autocomplete="current-password"
              class="w-full px-4 py-3.5 bg-white/8 border border-white/15 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-amber-400/60 focus:ring-1 focus:ring-amber-400/30 transition-all text-sm"
              @keyup.enter="handleLogin" />
          </div>
          <div v-if="errorMsg" class="text-red-400 text-xs text-left animate-slide-up px-1">
            ⚠ {{ errorMsg }}
          </div>
          <button type="submit" :disabled="loading"
            class="btn-click w-full py-3.5 rounded-lg font-semibold text-white transition-all duration-200 text-sm"
            :class="loading ? 'bg-gray-500 cursor-not-allowed opacity-60' : 'bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 hover:shadow-lg hover:shadow-amber-500/25'">
            {{ loading ? '登录中...' : '登 录' }}
          </button>
        </form>

        <!-- Divider -->
        <div class="flex items-center gap-3 my-6">
          <div class="flex-1 h-px bg-white/10" />
          <span class="text-xs text-gray-400">还没有账号？</span>
          <div class="flex-1 h-px bg-white/10" />
        </div>

        <!-- Register link -->
        <router-link to="/register"
          class="btn-click block w-full py-3 rounded-lg font-semibold transition-all duration-200 text-sm border border-amber-400/40 text-amber-400 hover:bg-amber-400/10">
          注 册 新 账 号
        </router-link>

        <p class="mt-4 text-[10px] text-gray-500">注册需管理员审核通过后方可登录</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

async function handleLogin() {
  loading.value = true; errorMsg.value = ''
  try {
    const res: any = await auth.login(username.value, password.value)
    if (res.code === 200) router.push('/dashboard')
    else errorMsg.value = res.message || '登录失败'
  } catch (e: any) { errorMsg.value = e?.message || '网络错误' }
  finally { loading.value = false }
}
</script>
