<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-glow">团队管理</h2>
      <button v-if="isAdmin" @click="showInvite=true" class="px-4 py-2 bg-cockpit-accent rounded-lg text-sm font-semibold hover:shadow-lg hover:shadow-cockpit-accent/30 transition-all animate-slide-up">
        + 创建子账号
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
      <div v-for="s in stats" :key="s.label" class="glass-panel p-3 text-center">
        <p class="text-xs text-cockpit-muted">{{ s.label }}</p>
        <p class="text-2xl font-bold data-value-glow">{{ s.value }}</p>
      </div>
    </div>

    <!-- Team Members Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="m in members" :key="m.id"
        class="glass-panel p-5 transition-all hover:scale-[1.02]"
        :class="m.role === 'admin' ? 'neon-border-active' : ''">
        <div class="flex items-start gap-4">
          <!-- Avatar -->
          <div class="w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold flex-shrink-0"
            :style="{ background: avatarColor(m.name) }">
            {{ (m.name || '?')[0].toUpperCase() }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <h3 class="font-semibold truncate">{{ m.name }}</h3>
              <span class="text-[10px] px-1.5 py-0.5 rounded-full"
                :class="m.role === 'admin' ? 'badge-urgent' : m.role === 'pm' ? 'badge-high' : 'badge-progress'">
                {{ roleLabel(m.role) }}
              </span>
            </div>
            <p class="text-xs text-cockpit-muted mb-2">@{{ m.username }}</p>
            <div class="flex flex-wrap gap-1 text-xs text-cockpit-muted">
              <span v-if="m.email">📧 {{ m.email }}</span>
              <span v-if="m.dept">🏢 {{ m.dept }}</span>
              <span v-if="m.phone">📱 {{ m.phone }}</span>
            </div>
            <!-- Role change (admin only) -->
            <div v-if="isAdmin && m.id !== currentUserId" class="flex gap-2 mt-3 pt-3 border-t border-cockpit-border/20">
              <select @change="changeRole(m, ($event.target as HTMLSelectElement).value)"
                class="text-xs px-2 py-1 bg-white/5 border border-cockpit-border/30 rounded">
                <option value="">更改角色</option>
                <option value="member">成员</option>
                <option value="pm">项目经理</option>
                <option value="admin">管理员</option>
                <option value="viewer">只读</option>
              </select>
              <button @click="deleteUser(m)" class="text-xs px-2 py-1 text-red-400 hover:bg-red-400/10 rounded transition-colors">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Invite Modal -->
    <div v-if="showInvite" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 animate-slide-up" @click.self="showInvite=false">
      <div class="glass-panel p-6 w-full max-w-md mx-4 neon-border">
        <h3 class="text-lg font-semibold text-glow mb-1">创建子账号</h3>
        <p class="text-xs text-cockpit-muted mb-4">为新成员创建一个系统账号</p>
        <form @submit.prevent="createSubAccount" class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-cockpit-muted block mb-1">用户名 *</label>
              <input v-model="form.username" required class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm focus:border-cockpit-gold focus:ring-1 focus:ring-cockpit-gold/30 outline-none transition-all" placeholder="英文/数字"/>
            </div>
            <div>
              <label class="text-xs text-cockpit-muted block mb-1">密码 *</label>
              <input v-model="form.password" type="password" required class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm focus:border-cockpit-gold outline-none transition-all" placeholder="至少6位"/>
            </div>
          </div>
          <div>
            <label class="text-xs text-cockpit-muted block mb-1">姓名 *</label>
            <input v-model="form.name" required class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm focus:border-cockpit-gold outline-none transition-all" placeholder="中文姓名"/>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-cockpit-muted block mb-1">邮箱</label>
              <input v-model="form.email" type="email" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm focus:border-cockpit-gold outline-none transition-all" placeholder="可选"/>
            </div>
            <div>
              <label class="text-xs text-cockpit-muted block mb-1">手机号</label>
              <input v-model="form.phone" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm focus:border-cockpit-gold outline-none transition-all" placeholder="可选"/>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-cockpit-muted block mb-1">部门</label>
              <input v-model="form.dept" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm focus:border-cockpit-gold outline-none transition-all" placeholder="如: 研发部"/>
            </div>
            <div>
              <label class="text-xs text-cockpit-muted block mb-1">角色</label>
              <select v-model="form.role" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm">
                <option value="member">成员</option>
                <option value="pm">项目经理</option>
                <option value="viewer">只读</option>
              </select>
            </div>
          </div>
          <div v-if="errorMsg" class="text-cockpit-accent text-xs animate-slide-up">⚠ {{ errorMsg }}</div>
          <div v-if="successMsg" class="text-green-400 text-xs animate-slide-up">✓ {{ successMsg }}</div>
          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="showInvite=false" class="px-4 py-2 rounded-lg text-sm text-cockpit-muted hover:text-cockpit-text transition-colors">取消</button>
            <button type="submit" :disabled="loading" class="px-5 py-2 bg-cockpit-accent rounded-lg text-sm font-semibold hover:bg-cockpit-accent/80 disabled:opacity-50 transition-all">
              {{ loading ? '创建中...' : '创建账号' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const members = ref<any[]>([])
const showInvite = ref(false)
const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')
const currentUserId = computed(() => auth.user?.id)
const isAdmin = computed(() => auth.user?.role === 'admin')

const form = ref({ username: '', password: '', name: '', email: '', phone: '', dept: '', role: 'member' })

const stats = computed(() => {
  const total = members.value.length
  const admins = members.value.filter(m => m.role === 'admin').length
  const pms = members.value.filter(m => m.role === 'pm').length
  const members_cnt = members.value.filter(m => m.role === 'member').length
  return [
    { label: '团队总人数', value: total },
    { label: '管理员', value: admins },
    { label: '项目经理', value: pms },
    { label: '团队成员', value: members_cnt },
  ]
})

const roleLabel = (r: string) => ({ admin: '管理员', pm: '项目经理', member: '成员', viewer: '只读' }[r] || r)
const avatarColor = (name: string) => {
  const colors = ['#FF4D2E','#F97316','#FBBF24','#22C55E','#3B82F6','#8B5CF6','#EC4899','#14B8A6']
  return colors[name?.charCodeAt(0) % colors.length] || colors[0]
}

onMounted(loadMembers)

async function loadMembers() {
  try { const r: any = await api.get('/users'); members.value = r.data?.items || [] } catch {}
}

async function createSubAccount() {
  loading.value = true; errorMsg.value = ''; successMsg.value = ''
  try {
    const r: any = await api.post('/users', form.value)
    if (r.code === 200) {
      successMsg.value = `子账号 ${form.value.username} 创建成功！`
      await loadMembers()
      setTimeout(() => { showInvite.value = false; successMsg.value = '' }, 1500)
      form.value = { username: '', password: '', name: '', email: '', phone: '', dept: '', role: 'member' }
    } else {
      errorMsg.value = r.message || '创建失败'
    }
  } catch (e: any) {
    errorMsg.value = e?.message || '网络错误'
  } finally { loading.value = false }
}

async function changeRole(member: any, newRole: string) {
  if (!newRole) return
  try { await api.put(`/users/${member.id}`, { role: newRole }); await loadMembers() } catch {}
}

async function deleteUser(member: any) {
  if (!confirm(`确定要删除用户 "${member.name}" 吗？此操作不可撤销。`)) return
  try { await api.delete(`/users/${member.id}`); await loadMembers() } catch {}
}
</script>
