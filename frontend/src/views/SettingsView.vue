<template>
  <div class="space-y-6 max-w-2xl">
    <h2 class="text-2xl font-bold text-glow">个人设置</h2>
    <!-- Profile -->
    <div class="glass-panel p-6">
      <h3 class="text-sm font-semibold text-cockpit-gold mb-4">个人信息</h3>
      <form @submit.prevent="saveProfile" class="space-y-3">
        <div class="grid grid-cols-2 gap-3">
          <div><label class="text-xs text-cockpit-muted block mb-1">用户名</label><input :value="profile.username" disabled class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm text-cockpit-muted"/></div>
          <div><label class="text-xs text-cockpit-muted block mb-1">姓名</label><input v-model="profile.name" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm focus:border-cockpit-gold outline-none transition-all"/></div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div><label class="text-xs text-cockpit-muted block mb-1">邮箱</label><input v-model="profile.email" type="email" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm focus:border-cockpit-gold outline-none transition-all"/></div>
          <div><label class="text-xs text-cockpit-muted block mb-1">手机</label><input v-model="profile.phone" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm focus:border-cockpit-gold outline-none transition-all"/></div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div><label class="text-xs text-cockpit-muted block mb-1">部门</label><input v-model="profile.dept" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm focus:border-cockpit-gold outline-none transition-all"/></div>
          <div><label class="text-xs text-cockpit-muted block mb-1">职位</label><input v-model="profile.title" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm focus:border-cockpit-gold outline-none transition-all"/></div>
        </div>
        <div class="flex justify-end"><button type="submit" class="px-4 py-2 bg-cockpit-accent rounded-lg text-sm">保存</button></div>
      </form>
    </div>
    <!-- Password -->
    <div class="glass-panel p-6">
      <h3 class="text-sm font-semibold text-cockpit-gold mb-4">修改密码</h3>
      <form @submit.prevent="changePwd" class="space-y-3">
        <div class="grid grid-cols-2 gap-3">
          <div><label class="text-xs text-cockpit-muted block mb-1">旧密码</label><input v-model="pwd.old" type="password" required class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm focus:border-cockpit-gold outline-none transition-all"/></div>
          <div><label class="text-xs text-cockpit-muted block mb-1">新密码</label><input v-model="pwd.new" type="password" required minlength="6" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm focus:border-cockpit-gold outline-none transition-all"/></div>
        </div>
        <div v-if="pwdMsg" class="text-xs" :class="pwdOk ? 'text-green-400' : 'text-cockpit-accent'">{{ pwdMsg }}</div>
        <div class="flex justify-end"><button type="submit" class="px-4 py-2 bg-cockpit-accent rounded-lg text-sm">更新密码</button></div>
      </form>
    </div>
    <!-- Display -->
    <div class="glass-panel p-6">
      <h3 class="text-sm font-semibold text-cockpit-gold mb-4">显示设置</h3>
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <span class="text-sm">界面字号</span>
          <div class="flex gap-1">
            <button v-for="s in ['small','medium','large']" :key="s" @click="prefs.font_size=s;savePrefs()"
              class="px-3 py-1.5 rounded text-xs transition-all"
              :class="prefs.font_size===s?'bg-cockpit-accent text-white':'bg-white/5 text-cockpit-muted hover:text-cockpit-text'">
              {{ s==='small'?'小':s==='large'?'大':'中' }}
            </button>
          </div>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-sm">界面语言</span>
          <div class="flex gap-1">
            <button v-for="l in [{k:'zh',v:'中文'},{k:'en',v:'English'}]" :key="l.k" @click="prefs.language=l.k;savePrefs()"
              class="px-3 py-1.5 rounded text-xs transition-all"
              :class="prefs.language===l.k?'bg-cockpit-accent text-white':'bg-white/5 text-cockpit-muted hover:text-cockpit-text'">
              {{ l.v }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'; import api from '@/api/client'
const profile = ref({ username:'', name:'', email:'', phone:'', dept:'', title:'' })
const pwd = ref({ old:'', new:'' }); const pwdMsg = ref(''); const pwdOk = ref(false)
const prefs = ref({ font_size:'medium', language:'zh' })

onMounted(async()=>{
  try {
    const [p,pf]:any[]=await Promise.all([api.get('/settings/profile'),api.get('/settings/preferences')])
    if(p.code===200) Object.assign(profile.value, p.data)
    if(pf.code===200) Object.assign(prefs.value, pf.data)
  } catch {}
})

async function saveProfile() {
  try { await api.put('/settings/profile', null, { params: profile.value }) } catch {}
}

async function changePwd() {
  pwdMsg.value=''; pwdOk.value=false
  try {
    const form=new FormData();form.append('old_password',pwd.old);form.append('new_password',pwd.new)
    const r:any=await api.post('/settings/change-password', form, {headers:{'Content-Type':'multipart/form-data'}})
    pwdMsg.value=r.message; pwdOk.value=r.code===200
    if(r.code===200) pwd.value={old:'',new:''}
  } catch(e:any){pwdMsg.value=e?.message||'错误'}
}

async function savePrefs() {
  try { await api.put('/settings/preferences', null, { params: prefs.value }) } catch {}
}
</script>
