<template>
  <div class="space-y-4">
    <h2 class="text-2xl font-bold text-glow">我的任务</h2>
    <!-- 5W Quick Create Bar -->
    <div class="glass-panel p-4">
      <div class="flex items-center gap-2 text-sm mb-3">
        <span class="text-cockpit-gold font-semibold">⚡ 快速新建任务 (5W法则)</span>
        <span class="text-[10px] text-cockpit-muted">What-Who-When-Where-Why</span>
      </div>
      <form @submit.prevent="quickCreate" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-2">
        <input v-model="qw.title" placeholder="What: 任务标题 *" required class="px-2.5 py-2 bg-white/5 border border-cockpit-border/30 rounded text-xs focus:border-cockpit-gold outline-none" />
        <select v-model="qw.assignee_id" class="px-2.5 py-2 bg-white/5 border border-cockpit-border/30 rounded text-xs">
          <option value="">Who: 负责人</option>
          <option v-for="u in users" :key="u.id" :value="u.id">{{ u.name }}</option>
        </select>
        <input v-model="qw.end_date" type="date" required class="px-2.5 py-2 bg-white/5 border border-cockpit-border/30 rounded text-xs focus:border-cockpit-gold outline-none" title="When: 计划完成时间" />
        <select v-model="qw.project_id" required class="px-2.5 py-2 bg-white/5 border border-cockpit-border/30 rounded text-xs">
          <option value="">Where: 所属项目 *</option>
          <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
        </select>
        <div class="flex gap-2 col-span-2 md:col-span-1">
          <select v-model="qw.status" class="px-2.5 py-2 bg-white/5 border border-cockpit-border/30 rounded text-xs flex-1">
            <option value="todo">待办</option><option value="pending">待处理</option>
            <option value="in_progress">进行中</option><option value="done">已完成</option>
          </select>
          <select v-model="qw.priority" class="px-2.5 py-2 bg-white/5 border border-cockpit-border/30 rounded text-xs w-20">
            <option value="medium">Why: P2</option><option value="urgent">P0急</option><option value="high">P1高</option><option value="low">P3低</option>
          </select>
          <button type="submit" class="px-3 py-2 bg-cockpit-accent rounded text-xs font-semibold hover:bg-cockpit-accent/80 whitespace-nowrap">+ 创建</button>
        </div>
      </form>
    </div>
    <!-- 4-column board -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="col in columns" :key="col.key"
        class="glass-panel p-3 min-h-[350px] flex flex-col"
        @dragover.prevent @drop.prevent="handleDrop(col.key, $event)">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm font-semibold" :class="col.color">{{ col.label }}</h3>
          <span class="text-xs px-2 py-0.5 rounded-full bg-white/10">{{ colTasks(col.key).length }}</span>
        </div>
        <div class="space-y-2 flex-1">
          <div v-for="t in colTasks(col.key)" :key="t.id" draggable="true"
            @dragstart="dragTask=t"
            @click="showDetail=t"
            class="p-3 rounded-lg border cursor-pointer transition-all hover:scale-[1.02] group"
            :class="[col.border, isOverdue(t) ? 'border-cockpit-accent/50 bg-cockpit-accent/8 alert-pulse-border' : 'border-cockpit-border/20 bg-white/3']">
            <div class="flex items-start justify-between gap-2 mb-1">
              <p class="text-sm font-medium leading-snug">{{ t.title }}</p>
              <span class="text-[10px] px-1.5 py-0.5 rounded flex-shrink-0" :class="priorityBadge(t.priority)">{{ t.priority }}</span>
            </div>
            <div class="flex flex-wrap gap-1 text-[10px] text-cockpit-muted mb-1">
              <span>👤 {{ t.assignee_name || '未分配' }}</span>
              <span>📁 {{ t.project_name || 'P#'+t.project_id }}</span>
            </div>
            <div class="flex justify-between items-center text-[10px]">
              <span :class="isOverdue(t) ? 'text-cockpit-accent font-semibold' : 'text-cockpit-muted'">
                {{ isOverdue(t) ? '⚠ 逾期 '+overdueDays(t)+'天' : '📅 截止: '+formatDate(t.end_date) }}
              </span>
              <span class="text-cockpit-muted opacity-0 group-hover:opacity-100 transition-opacity">⏱ {{ t.estimated_hours || 0 }}h</span>
            </div>
          </div>
          <p v-if="colTasks(col.key).length===0" class="text-[10px] text-cockpit-muted text-center py-10">
            拖拽任务至此列
          </p>
        </div>
        <!-- Column +New button -->
        <button @click="openCreate(col.key)"
          class="mt-2 w-full py-2 rounded-lg border border-dashed border-cockpit-border/30 text-[10px] text-cockpit-muted hover:border-cockpit-gold/50 hover:text-cockpit-gold transition-all">
          + 新建「{{ col.label }}」任务
        </button>
      </div>
    </div>
    <!-- 5W Create Modal -->
    <div v-if="showCreateForm" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50" @click.self="showCreateForm=false">
      <div class="glass-panel p-6 w-full max-w-xl mx-4 neon-border animate-slide-up max-h-[90vh] overflow-auto">
        <h3 class="text-lg font-semibold text-glow mb-1">新建任务 — 5W法则</h3>
        <p class="text-xs text-cockpit-muted mb-4">状态: {{ statusLabel(createForm.status) }}</p>
        <form @submit.prevent="doCreate" class="space-y-3">
          <div><label class="text-xs text-cockpit-muted block mb-1">What · 任务标题 *</label><input v-model="createForm.title" required class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded text-sm focus:border-cockpit-gold outline-none" placeholder="要做什么？"/></div>
          <div><label class="text-xs text-cockpit-muted block mb-1">What · 任务描述</label><textarea v-model="createForm.description" rows="2" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded text-sm focus:border-cockpit-gold outline-none" placeholder="验收标准 / 详细说明"/></div>
          <div class="grid grid-cols-2 gap-3">
            <div><label class="text-xs text-cockpit-muted block mb-1">Who · 负责人</label><select v-model="createForm.assignee_id" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded text-sm"><option value="">选择...</option><option v-for="u in users" :key="u.id" :value="u.id">{{ u.name }}</option></select></div>
            <div><label class="text-xs text-cockpit-muted block mb-1">When · 计划开始</label><input v-model="createForm.start_date" type="date" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded text-sm"/></div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div><label class="text-xs text-cockpit-muted block mb-1">When · 计划完成 *</label><input v-model="createForm.end_date" type="date" required class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded text-sm"/></div>
            <div><label class="text-xs text-cockpit-muted block mb-1">When · 预估工时(h)</label><input v-model="createForm.estimated_hours" type="number" step="0.5" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded text-sm"/></div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div><label class="text-xs text-cockpit-muted block mb-1">Where · 所属项目 *</label><select v-model="createForm.project_id" required class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded text-sm"><option value="">选择...</option><option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option></select></div>
            <div><label class="text-xs text-cockpit-muted block mb-1">Why · 优先级</label><select v-model="createForm.priority" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded text-sm"><option value="medium">P2-中</option><option value="urgent">P0-紧急</option><option value="high">P1-高</option><option value="low">P3-低</option></select></div>
          </div>
          <div v-if="createError" class="text-xs text-cockpit-accent animate-slide-up">⚠ {{ createError }}</div>
          <div class="flex justify-end gap-3 pt-2"><button type="button" @click="showCreateForm=false" class="px-4 py-2 rounded text-sm text-cockpit-muted">取消</button><button type="submit" class="px-5 py-2 bg-cockpit-accent rounded text-sm font-semibold">创建任务</button></div>
        </form>
      </div>
    </div>
    <!-- Detail -->
    <div v-if="showDetail" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50" @click.self="showDetail=null">
      <div class="glass-panel p-6 w-full max-w-lg mx-4 animate-slide-up max-h-[85vh] overflow-auto">
        <h3 class="text-lg font-semibold mb-1">{{ showDetail.title }}</h3>
        <p class="text-xs text-cockpit-muted mb-3">{{ showDetail.description || '暂无描述' }}</p>
        <div class="grid grid-cols-2 gap-2 text-xs mb-4">
          <div><span class="text-cockpit-muted">状态: </span>{{ statusLabel(showDetail.status) }}</div>
          <div><span class="text-cockpit-muted">优先级: </span>{{ showDetail.priority }}</div>
          <div><span class="text-cockpit-muted">负责人: </span>{{ showDetail.assignee_name || '-' }}</div>
          <div><span class="text-cockpit-muted">项目: </span>{{ showDetail.project_name || '-' }}</div>
          <div><span class="text-cockpit-muted">开始: </span>{{ formatDate(showDetail.start_date) }}</div>
          <div><span class="text-cockpit-muted">截止: </span>{{ formatDate(showDetail.end_date) }}</div>
          <div><span class="text-cockpit-muted">预估: </span>{{ showDetail.estimated_hours || 0 }}h</div>
          <div><span class="text-cockpit-muted">实际: </span>{{ showDetail.actual_hours || 0 }}h</div>
        </div>
        <div class="flex gap-2 border-t border-cockpit-border/20 pt-3">
          <select @change="changeStatus(($event.target as HTMLSelectElement).value)" class="text-xs px-2 py-1.5 bg-white/5 border border-cockpit-border/30 rounded"><option value="">切换状态</option><option v-for="c in columns" :key="c.key" :value="c.key">{{ c.label }}</option></select>
          <button @click="showDetail=null" class="ml-auto px-3 py-1.5 bg-white/10 rounded text-xs">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'; import api from '@/api/client'

const columns = [
  { key: 'todo', label: '待办', color: 'text-slate-400', border: 'border-slate-500/20' },
  { key: 'pending', label: '待处理', color: 'text-yellow-400', border: 'border-yellow-500/20' },
  { key: 'in_progress', label: '进行中', color: 'text-blue-400', border: 'border-blue-500/20' },
  { key: 'done', label: '已完成', color: 'text-green-400', border: 'border-green-500/20' },
]
const allTasks = ref<any[]>([]); const users = ref<any[]>([]); const projects = ref<any[]>([])
const showDetail = ref<any>(null); const dragTask = ref<any>(null)
const showCreateForm = ref(false); const createError = ref('')
const createForm = ref({ title:'',description:'',assignee_id:'',start_date:'',end_date:'',estimated_hours:'',project_id:'',priority:'medium',status:'todo' })
const qw = ref({ title:'',assignee_id:'',end_date:'',project_id:'',priority:'medium',status:'todo' })

const statusLabel=(s:string)=>({todo:'待办',pending:'待处理',in_progress:'进行中',done:'已完成',review:'审核中',blocked:'阻塞'}[s]||s)
const priorityBadge=(p:string)=>({urgent:'badge-urgent',high:'badge-high',medium:'badge-todo',low:'badge-progress'}[p]||'badge-todo')
const formatDate=(d:string)=>d ? d.split('T')[0] : '-'
const isOverdue=(t:any)=>t.end_date && new Date(t.end_date) < new Date() && t.status !== 'done'
const overdueDays=(t:any)=>{if(!t.end_date)return 0;return Math.floor((Date.now()-new Date(t.end_date).getTime())/86400000)}
const colTasks=(key:string)=>{const ts=allTasks.value.filter((t:any)=>t.status===key);return ts.slice(0,12)}

onMounted(async()=>{
  try {
    const [tr,ur,pr]:any[]=await Promise.all([api.get('/tasks/my'),api.get('/users'),api.get('/projects')])
    allTasks.value=tr.data||[];users.value=ur.data?.items||[];projects.value=pr.data?.items||[]
  } catch {}
})

async function quickCreate() {
  if (!qw.value.title||!qw.value.project_id||!qw.value.end_date) return
  try {
    const r:any=await api.post('/tasks',{...qw.value,estimated_hours:0,description:'',start_date:new Date().toISOString().split('T')[0],plan_id:+qw.value.project_id})
    if(r.code===200){allTasks.value.unshift(r.data);qw.value={title:'',assignee_id:'',end_date:'',project_id:'',priority:'medium',status:'todo'}}
  } catch {}
}

function openCreate(status:string){createForm.value.status=status;showCreateForm.value=true}
async function doCreate(){
  createError.value=''
  if(!createForm.value.title||!createForm.value.project_id||!createForm.value.end_date){createError.value='What/Where/When 为必填字段';return}
  try{
    const r:any=await api.post('/tasks',{...createForm.value,plan_id:+createForm.value.project_id,estimated_hours:Number(createForm.value.estimated_hours)||0,description:createForm.value.description||''})
    if(r.code===200){allTasks.value.unshift(r.data);showCreateForm.value=false}
  }catch(e:any){createError.value=e?.message||'创建失败'}
}

async function handleDrop(status:string,e:DragEvent){if(!dragTask.value)return;try{await api.patch(`/tasks/${dragTask.value.id}/status`,{status});dragTask.value.status=status}catch{}}
async function changeStatus(status:string){if(!status||!showDetail.value)return;try{await api.patch(`/tasks/${showDetail.value.id}/status`,{status});showDetail.value.status=status;showDetail.value=null}catch{}}
</script>
