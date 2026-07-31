<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-glow">团队管理</h2>
      <button v-if="isAdmin" @click="showInvite=true" class="btn-click px-4 py-2 bg-cockpit-accent rounded-lg text-sm font-semibold hover:shadow-lg hover:shadow-cockpit-accent/30 transition-all">+ 创建子账号</button>
    </div>

    <!-- Pending approvals (admin only) -->
    <div v-if="isAdmin && pendingUsers.length" class="glass-panel p-5 border-cockpit-gold/40 neon-border">
      <h3 class="text-sm font-semibold text-cockpit-gold mb-3 flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-cockpit-gold alert-pulse" />
        待审核注册 ({{ pendingUsers.length }})
      </h3>
      <div class="space-y-2">
        <div v-for="u in pendingUsers" :key="u.id" class="flex items-center gap-3 p-3 rounded-lg bg-cockpit-gold/5 border border-cockpit-gold/20">
          <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0" :style="{background:avColor(u.name)}">{{u.name[0]}}</div>
          <div class="flex-1 min-w-0 text-sm">
            <span class="font-medium">{{u.name}}</span>
            <span class="text-cockpit-muted ml-2 text-xs">{{u.gender}} · {{u.age}}岁 · {{u.phone}}</span>
          </div>
          <button @click="approve(u.id)" class="btn-click px-3 py-1.5 bg-green-500/20 text-green-400 rounded text-xs font-semibold hover:bg-green-500/30 transition-all duration-200">✓ 通过</button>
          <button @click="reject(u.id)" class="btn-click px-3 py-1.5 bg-red-500/20 text-red-400 rounded text-xs font-semibold hover:bg-red-500/30 transition-all duration-200">✕ 拒绝</button>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
      <div v-for="s in stats" :key="s.label" class="glass-panel p-3 text-center">
        <p class="text-xs text-cockpit-muted">{{ s.label }}</p>
        <p class="text-2xl font-bold data-value-glow">{{ s.value }}</p>
      </div>
    </div>

    <!-- Team Members -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="m in activeMembers" :key="m.id" class="glass-panel p-5 transition-all hover:scale-[1.02]" :class="m.role==='admin'?'neon-border-active':''">
        <div class="flex items-start gap-4">
          <div class="w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold flex-shrink-0" :style="{background:avColor(m.name)}">{{(m.name||'?')[0]}}</div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <h3 class="font-semibold truncate">{{ m.name }}</h3>
              <span class="text-[10px] px-1.5 py-0.5 rounded-full" :class="roleBadge(m.role)">{{ roleLabel(m.role) }}</span>
            </div>
            <p class="text-xs text-cockpit-muted">@{{ m.username }}</p>
            <div class="flex flex-wrap gap-1 text-xs text-cockpit-muted mt-1">
              <span v-if="m.phone">📱 {{ m.phone }}</span>
              <span v-if="m.dept">🏢 {{ m.dept }}</span>
            </div>
            <!-- Admin actions -->
            <div v-if="isAdmin && m.id!==currentUserId" class="flex gap-2 mt-3 pt-3 border-t border-cockpit-border/20">
              <select @change="changeRole(m,($event.target as HTMLSelectElement).value)" class="text-xs px-2 py-1 bg-white/5 border border-cockpit-border/30 rounded">
                <option value="">角色</option><option value="member">成员</option><option value="pm">PM</option><option value="admin">管理员</option><option value="viewer">只读</option>
              </select>
              <button @click="deleteUser(m)" class="btn-click text-xs px-2 py-1 text-red-400 hover:bg-red-400/10 rounded transition-colors">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Invite Modal -->
    <div v-if="showInvite" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50" @click.self="showInvite=false">
      <div class="glass-panel p-6 w-full max-w-md mx-4 neon-border animate-slide-up max-h-[90vh] overflow-auto">
        <h3 class="text-lg font-semibold text-glow mb-4">创建子账号（管理员直接生效）</h3>
        <form @submit.prevent="createAccount" class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div><label class="text-xs text-cockpit-muted">用户名 *</label><input v-model="form.username" required class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded text-sm"/></div>
            <div><label class="text-xs text-cockpit-muted">密码 *</label><input v-model="form.password" type="password" required class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded text-sm"/></div>
          </div>
          <div><label class="text-xs text-cockpit-muted">姓名 *</label><input v-model="form.name" required class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded text-sm"/></div>
          <div class="grid grid-cols-2 gap-3">
            <div><label class="text-xs text-cockpit-muted">邮箱</label><input v-model="form.email" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded text-sm"/></div>
            <div><label class="text-xs text-cockpit-muted">手机</label><input v-model="form.phone" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded text-sm"/></div>
          </div>
          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="showInvite=false" class="btn-click px-4 py-2 rounded text-sm text-cockpit-muted">取消</button>
            <button type="submit" class="btn-click px-4 py-2 bg-cockpit-accent rounded text-sm">创建</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'; import api from '@/api/client'; import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()
const members = ref<any[]>([]); const pendingUsers = ref<any[]>([])
const showInvite = ref(false); const currentUserId = computed(()=>auth.user?.id); const isAdmin = computed(()=>auth.user?.role==='admin')
const form = ref({username:'',password:'',name:'',email:'',phone:''})
const activeMembers = computed(()=>members.value.filter(m=>m.status==='active'))
const stats = computed(()=>{
  const a=activeMembers.value; return [
    {label:'团队人数',value:a.length},{label:'管理员',value:a.filter(m=>m.role==='admin').length},{label:'待审核',value:pendingUsers.value.length}
  ]
})
const roleLabel=(r:string)=>({admin:'管理员',pm:'项目经理',member:'成员',viewer:'只读'}[r]||r)
const roleBadge=(r:string)=>({admin:'badge-urgent',pm:'badge-high',member:'badge-progress',viewer:'badge-todo'}[r]||'badge-todo')
const avColor=(n:string)=>{const c=['#FF4D2E','#F97316','#FBBF24','#22C55E','#3B82F6','#8B5CF6','#EC4899'];return c[n?.charCodeAt(0)%c.length]||c[0]}

onMounted(loadData)
async function loadData(){try{const[r,p]:any[]=await Promise.all([api.get('/users'),api.get('/users/pending/list')]);members.value=r.data?.items||[];pendingUsers.value=p.data||[]}catch{}}
async function createAccount(){
  try{const r:any=await api.post('/users',{...form.value,role:'member'});if(r.code===200){showInvite.value=false;form.value={username:'',password:'',name:'',email:'',phone:''};await loadData()}}catch{}
}
async function approve(id:number){try{await api.put(`/users/${id}/approve`);await loadData()}catch{}}
async function reject(id:number){try{await api.put(`/users/${id}/reject`);await loadData()}catch{}}
async function changeRole(m:any,role:string){if(!role)return;try{await api.put(`/users/${m.id}`,{role});await loadData()}catch{}}
async function deleteUser(m:any){if(!confirm('删除 '+m.name+'?不可撤销。'))return;try{await api.delete('/users/'+m.id);await loadData()}catch{}}
</script>
