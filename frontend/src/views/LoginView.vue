<template>
  <div class="min-h-screen flex items-center justify-center bg-cockpit-bg relative overflow-hidden">
    <!-- Background effects -->
    <div class="absolute inset-0 bg-gradient-to-br from-cockpit-accent/5 via-transparent to-cockpit-gold/5" />
    <div class="absolute inset-0" style="background: radial-gradient(ellipse at center, rgba(255,77,46,0.08) 0%, transparent 70%)" />

    <div class="relative w-full max-w-md mx-4">
      <div class="glass-panel p-8 text-center">
        <h1 class="text-3xl font-bold text-glow mb-2 tracking-wider">晴天天</h1>
        <p class="text-cockpit-muted mb-8">Atlas PM — 项目管理作战驾驶舱</p>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <input v-model="username" type="text" placeholder="用户名"
              class="w-full px-4 py-3 bg-white/5 border border-cockpit-border/30 rounded-lg text-cockpit-text placeholder-cockpit-muted focus:outline-none focus:border-cockpit-gold focus:ring-1 focus:ring-cockpit-gold/30 transition-all" />
          </div>
          <div>
            <input v-model="password" type="password" placeholder="密码"
              class="w-full px-4 py-3 bg-white/5 border border-cockpit-border/30 rounded-lg text-cockpit-text placeholder-cockpit-muted focus:outline-none focus:border-cockpit-gold focus:ring-1 focus:ring-cockpit-gold/30 transition-all"
              @keyup.enter="handleLogin" />
          </div>
          <div v-if="errorMsg" class="text-cockpit-accent text-sm text-left animate-slide-up">
            ⚠ {{ errorMsg }}
          </div>
          <button type="submit" :disabled="loading"
            class="w-full py-3 rounded-lg font-semibold text-white transition-all duration-300"
            :class="loading ? 'bg-cockpit-muted cursor-not-allowed' : 'bg-cockpit-accent hover:bg-cockpit-accent/80 hover:shadow-lg hover:shadow-cockpit-accent/25'">
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>

        <p class="mt-6 text-xs text-cockpit-muted">默认账号: admin / admin</p>
        <p class="mt-3">
          <button @click="toggleRegister" class="text-xs text-cockpit-gold hover:text-cockpit-accent transition-colors">
            {{ showRegister ? '已有账号？去登录' : '注册新账号' }}
          </button>
        </p>

        <!-- Register form -->
        <form v-if="showRegister" @submit.prevent="handleRegister" class="mt-6 space-y-3 border-t border-cockpit-border/20 pt-6">
          <input v-model="regName" type="text" placeholder="姓名" required
            class="w-full px-4 py-2.5 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm text-cockpit-text placeholder-cockpit-muted focus:outline-none focus:border-cockpit-gold transition-all" />
          <input v-model="regEmail" type="email" placeholder="邮箱（选填）"
            class="w-full px-4 py-2.5 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm text-cockpit-text placeholder-cockpit-muted focus:outline-none focus:border-cockpit-gold transition-all" />
          <button type="submit" :disabled="regLoading"
            class="w-full py-2.5 rounded-lg text-sm font-semibold text-white bg-cockpit-gold/80 hover:bg-cockpit-gold transition-all">
            {{ regLoading ? '注册中...' : '注册' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'

const router = useRouter()
const auth = useAuthStore()

const username = ref('admin')
const password = ref('admin123')
const loading = ref(false)
const errorMsg = ref('')

const showRegister = ref(false)
const regName = ref('')
const regEmail = ref('')
const regLoading = ref(false)

async function handleLogin() {
  loading.value = true; errorMsg.value = ''
  try {
    const res: any = await auth.login(username.value, password.value)
    if (res.code === 200) router.push('/dashboard')
    else errorMsg.value = res.message || '登录失败'
  } catch (e: any) {
    errorMsg.value = e?.message || '网络错误，请重试'
  } finally { loading.value = false }
}

async function handleRegister() {
  regLoading.value = true; errorMsg.value = ''
  try {
    const res: any = await authApi.register({
      username: username.value,
      password: password.value,
      name: regName.value,
      email: regEmail.value,
    })
    if (res.code === 200) {
      const loginRes: any = await auth.login(username.value, password.value)
      if (loginRes.code === 200) router.push('/dashboard')
    } else errorMsg.value = res.message || '注册失败'
  } catch (e: any) {
    errorMsg.value = e?.message || '网络错误'
  } finally { regLoading.value = false }
}

function toggleRegister() {
  showRegister.value = !showRegister.value
  errorMsg.value = ''
}
</script>
