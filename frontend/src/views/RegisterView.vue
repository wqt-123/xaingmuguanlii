<template>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden py-8">
    <!-- Background image same as login -->
    <div class="absolute inset-0 z-0">
      <img src="/qingtian/images/login-bg.webp" alt=""
        class="w-full h-full object-cover" />
      <div class="absolute inset-0 bg-gradient-to-br from-black/80 via-black/65 to-black/75" />
    </div>

    <!-- Register Card -->
    <div class="relative z-10 w-full max-w-lg mx-4 animate-slide-up">
      <div class="backdrop-blur-xl rounded-2xl p-8"
        style="background: rgba(17,24,39,0.7); border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 8px 40px rgba(0,0,0,0.5);">

        <!-- Header -->
        <div class="text-center mb-6">
          <h1 class="text-2xl font-bold text-white tracking-wider drop-shadow-lg">注册账号</h1>
          <p class="text-xs text-gray-400 mt-1">填写以下信息，提交后等待管理员审核通过即可登录</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleRegister" class="space-y-3">
          <!-- Name -->
          <div>
            <label class="text-xs text-gray-400 block mb-1">姓名 <span class="text-red-400">*</span></label>
            <input v-model="form.name" placeholder="请输入真实姓名" required autocomplete="name"
              class="w-full px-4 py-3 bg-white/8 border border-white/15 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:border-amber-400/60 focus:ring-1 focus:ring-amber-400/30 transition-all" />
          </div>

          <!-- Gender + Age -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-gray-400 block mb-1">性别 <span class="text-red-400">*</span></label>
              <select v-model="form.gender" required
                class="w-full px-4 py-3 bg-white/8 border border-white/15 rounded-lg text-white text-sm focus:outline-none focus:border-amber-400/60 transition-all">
                <option value="" class="bg-gray-800">请选择</option>
                <option value="男" class="bg-gray-800">男</option>
                <option value="女" class="bg-gray-800">女</option>
                <option value="其他" class="bg-gray-800">其他</option>
              </select>
            </div>
            <div>
              <label class="text-xs text-gray-400 block mb-1">年龄 <span class="text-red-400">*</span></label>
              <input v-model="form.age" type="number" placeholder="请输入年龄" required min="1" max="150"
                class="w-full px-4 py-3 bg-white/8 border border-white/15 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:border-amber-400/60 transition-all" />
            </div>
          </div>

          <!-- Username -->
          <div>
            <label class="text-xs text-gray-400 block mb-1">用户名 <span class="text-red-400">*</span></label>
            <input v-model="form.username" placeholder="设置登录用户名" required autocomplete="new-username"
              class="w-full px-4 py-3 bg-white/8 border border-white/15 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:border-amber-400/60 transition-all" />
          </div>

          <!-- Phone -->
          <div>
            <label class="text-xs text-gray-400 block mb-1">手机号 <span class="text-red-400">*</span></label>
            <input v-model="form.phone" type="tel" placeholder="请输入手机号" required autocomplete="tel"
              class="w-full px-4 py-3 bg-white/8 border border-white/15 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:border-amber-400/60 transition-all" />
          </div>

          <!-- Password -->
          <div>
            <label class="text-xs text-gray-400 block mb-1">密码 <span class="text-red-400">*</span></label>
            <input v-model="form.password" type="password" placeholder="至少8位，需包含字母和数字" required autocomplete="new-password"
              class="w-full px-4 py-3 bg-white/8 border border-white/15 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:border-amber-400/60 transition-all" />
            <p class="text-[10px] text-gray-500 mt-1">至少8位，必须包含字母和数字</p>
          </div>

          <!-- Email (Optional) -->
          <div>
            <label class="text-xs text-gray-400 block mb-1">邮箱 <span class="text-gray-500">(选填)</span></label>
            <input v-model="form.email" type="email" placeholder="请输入邮箱（选填）" autocomplete="email"
              class="w-full px-4 py-3 bg-white/8 border border-white/15 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:border-amber-400/60 transition-all" />
          </div>

          <!-- Message -->
          <div v-if="msg" class="text-xs px-3 py-2.5 rounded-lg" :class="ok ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'">
            {{ msg }}
          </div>

          <!-- Buttons -->
          <div class="flex gap-3 pt-3">
            <router-link to="/login"
              class="btn-click flex-1 py-3 rounded-lg text-sm text-center border border-white/20 text-gray-400 hover:text-white hover:border-white/30 transition-all duration-200">
              返回登录
            </router-link>
            <button type="submit" :disabled="loading"
              class="btn-click flex-1 py-3 rounded-lg text-sm font-semibold text-white transition-all duration-200 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400"
              :class="loading ? 'opacity-50' : ''">
              {{ loading ? '提交中...' : '提交注册' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { authApi } from '@/api/auth'

const form = ref({ name:'',gender:'',age:'',username:'',phone:'',password:'',email:'' })
const loading = ref(false)
const msg = ref('')
const ok = ref(false)

async function handleRegister() {
  loading.value = true; msg.value = ''; ok.value = false
  try {
    const r: any = await authApi.register({
      username: form.value.username, password: form.value.password,
      name: form.value.name, gender: form.value.gender,
      age: Number(form.value.age), phone: form.value.phone,
      email: form.value.email,
    })
    if (r.code === 200) {
      msg.value = '注册申请已提交成功！请等待管理员审核通过后登录。'
      ok.value = true
      form.value = { name:'',gender:'',age:'',username:'',phone:'',password:'',email:'' }
    } else {
      msg.value = r.message || '注册失败'
    }
  } catch (e: any) { msg.value = e?.message || '网络错误' }
  finally { loading.value = false }
}
</script>
