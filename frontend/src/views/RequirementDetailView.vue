<template>
  <div class="space-y-6">
    <button @click="$router.push('/requirements')" class="text-sm text-cockpit-gold hover:text-cockpit-accent transition-colors">← 返回需求池</button>
    <div v-if="req" class="glass-panel p-6">
      <div class="flex justify-between items-start mb-4">
        <div>
          <span class="text-xs text-cockpit-muted">REQ-{{ req.id }}</span>
          <h2 class="text-xl font-bold mt-1">{{ req.title }}</h2>
        </div>
        <span class="px-3 py-1 rounded text-xs font-semibold" :class="statusColor(req.status)">{{ statusLabel(req.status) }}</span>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 text-sm">
        <div><span class="text-cockpit-muted">优先级: </span><span :class="priorityColor(req.priority)">{{ req.priority }}</span></div>
        <div><span class="text-cockpit-muted">来源: </span>{{ sourceLabel(req.source) }}</div>
        <div><span class="text-cockpit-muted">预估: </span>{{ req.estimated_effort || '-' }} 人天</div>
        <div><span class="text-cockpit-muted">版本: </span>{{ req.version || '-' }}</div>
      </div>
      <div class="mb-4"><h4 class="text-sm font-semibold text-cockpit-gold mb-2">需求描述</h4><p class="text-sm text-cockpit-muted whitespace-pre-wrap">{{ req.description || '暂无描述' }}</p></div>
      <!-- Actions -->
      <div class="flex gap-2 border-t border-cockpit-border/20 pt-4">
        <button @click="submitReview" v-if="req.status==='draft'" class="px-3 py-1.5 bg-cockpit-gold/80 rounded text-xs">提交评审</button>
        <button @click="showChangeForm=true" class="px-3 py-1.5 bg-white/10 rounded text-xs hover:bg-white/20">变更申请</button>
      </div>
      <!-- Changes -->
      <div v-if="changes.length" class="mt-6 border-t border-cockpit-border/20 pt-4">
        <h4 class="text-sm font-semibold text-cockpit-gold mb-2">变更记录</h4>
        <div v-for="c in changes" :key="c.id" class="p-2.5 rounded bg-white/3 border border-cockpit-border/20 mb-2 text-sm">
          <span>{{ c.change_desc }}</span>
          <span class="ml-2 text-xs text-cockpit-muted">- {{ c.created_at?.split('T')[0] }}</span>
          <span class="ml-2 px-1.5 py-0.5 rounded text-xs" :class="c.status==='approved'?'badge-done':c.status==='rejected'?'badge-urgent':'badge-progress'">{{ c.status === 'approved' ? '已批准' : c.status === 'rejected' ? '已驳回' : '待审批' }}</span>
        </div>
      </div>
    </div>
    <!-- Change form modal -->
    <div v-if="showChangeForm" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50" @click.self="showChangeForm=false">
      <div class="glass-panel p-6 w-full max-w-md"><h3 class="text-lg font-semibold mb-4">需求变更申请</h3>
        <form @submit.prevent="submitChange" class="space-y-3">
          <textarea v-model="changeForm.change_desc" placeholder="变更说明 *" required rows="2" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm"/>
          <input v-model="changeForm.reason" placeholder="变更原因" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm"/>
          <textarea v-model="changeForm.impact" placeholder="影响范围" rows="2" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm"/>
          <div class="flex justify-end gap-3"><button type="button" @click="showChangeForm=false" class="px-4 py-2 rounded-lg text-sm text-cockpit-muted">取消</button><button type="submit" class="px-4 py-2 bg-cockpit-accent rounded-lg text-sm">提交</button></div>
        </form>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'; import { useRoute } from 'vue-router'; import api from '@/api/client'
const route = useRoute(); const req = ref<any>(null); const changes = ref<any[]>([]); const showChangeForm = ref(false)
const changeForm = ref({ change_desc: '', reason: '', impact: '' })
const statusLabel=(s:string)=>({draft:'草稿',pending_review:'待评审',approved:'已通过',rejected:'已驳回',in_dev:'开发中',done:'已完成'}[s]||s)
const statusColor=(s:string)=>({draft:'badge-todo',approved:'badge-done',done:'badge-done',in_dev:'badge-progress',rejected:'badge-blocked',pending_review:'badge-high'}[s]||'badge-todo')
const priorityColor=(p:string)=>({P0:'text-red-400',P1:'text-orange-400',P2:'text-yellow-400',P3:'text-green-400'}[p]||'')
const sourceLabel=(s:string)=>({product:'产品规划',user_feedback:'用户反馈',business:'业务提出',tech:'技术优化',other:'其他'}[s]||s)
onMounted(async()=>{try{const id=route.params.id as string;const[rr,cr]:any[]=await Promise.all([api.get('/requirements/'+id),api.get('/requirements/'+id+'/changes')]);req.value=rr.data;changes.value=cr.data||[]}catch{}})
async function submitReview(){try{const id=route.params.id as string;await api.post('/requirements/'+id+'/submit_review');req.value.status='pending_review'}catch{}}
async function submitChange(){try{const id=route.params.id as string;const r:any=await api.post('/requirements/'+id+'/change',changeForm.value);if(r.code===200){changes.value.unshift(r.data);showChangeForm.value=false}}catch{}}
</script>
