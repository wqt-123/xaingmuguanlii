<template>
  <div class="space-y-4">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-glow">消息中心</h2>
      <button @click="showCompose=true" class="px-4 py-2 bg-cockpit-gold/80 rounded-lg text-sm font-semibold hover:bg-cockpit-gold transition-all">+ 发送消息</button>
    </div>
    <!-- Tabs -->
    <div class="flex gap-1 border-b border-cockpit-border/20 pb-0">
      <button @click="tab='inbox'" class="px-4 py-2 text-sm rounded-t-lg transition-colors" :class="tab==='inbox'?'bg-cockpit-accent text-white':'text-cockpit-muted hover:text-cockpit-text'">收件箱</button>
      <button @click="tab='sent'" class="px-4 py-2 text-sm rounded-t-lg transition-colors" :class="tab==='sent'?'bg-cockpit-accent text-white':'text-cockpit-muted hover:text-cockpit-text'">已发送</button>
    </div>
    <!-- Messages -->
    <div v-if="messages.length" class="space-y-1">
      <div v-for="m in messages" :key="m.id" @click="openMsg(m)"
        class="glass-panel p-3.5 cursor-pointer transition-all hover:border-cockpit-gold/40"
        :class="!m.is_read && tab==='inbox' ? 'border-l-2 border-l-cockpit-accent bg-cockpit-accent/3' : ''">
        <div class="flex items-center justify-between gap-3">
          <div class="flex items-center gap-2 min-w-0">
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
              :style="{background:avatarColor(tab==='inbox' ? m.sender_name : m.receiver_name)}">
              {{ (tab==='inbox' ? m.sender_name : m.receiver_name || '?')[0].toUpperCase() }}
            </div>
            <div class="min-w-0">
              <p class="text-sm font-medium truncate" :class="!m.is_read && tab==='inbox' ? '' : 'text-cockpit-muted'">
                {{ m.subject || '(无主题)' }}
              </p>
              <p class="text-xs text-cockpit-muted truncate">{{ tab==='inbox' ? m.sender_name : '发给: '+m.receiver_name }} · {{ formatTime(m.sent_at) }}</p>
            </div>
          </div>
          <span v-if="!m.is_read && tab==='inbox'" class="w-2 h-2 rounded-full bg-cockpit-accent flex-shrink-0 alert-pulse" />
        </div>
      </div>
    </div>
    <p v-else class="text-cockpit-muted text-center py-12">{{ tab==='inbox' ? '收件箱为空' : '暂无已发送消息' }}</p>
    <!-- Message detail -->
    <div v-if="detailMsg" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50" @click.self="detailMsg=null">
      <div class="glass-panel p-6 w-full max-w-xl mx-4 neon-border animate-slide-up">
        <div class="flex justify-between items-start mb-4">
          <div>
            <p class="text-xs text-cockpit-muted">{{ tab==='inbox' ? '来自: '+detailMsg.sender_name : '发给: '+detailMsg.receiver_name }}</p>
            <h3 class="text-lg font-semibold mt-1">{{ detailMsg.subject || '(无主题)' }}</h3>
          </div>
          <span class="text-[10px] text-cockpit-muted">{{ formatTime(detailMsg.sent_at) }}</span>
        </div>
        <p class="text-sm text-cockpit-muted whitespace-pre-wrap mb-6 leading-relaxed">{{ detailMsg.body }}</p>
        <div class="flex justify-end gap-2 border-t border-cockpit-border/20 pt-4">
          <button v-if="tab==='inbox'" @click="replyMsg" class="px-3 py-1.5 bg-cockpit-gold/20 text-cockpit-gold rounded text-xs">回复</button>
          <button @click="detailMsg=null" class="px-3 py-1.5 bg-white/10 rounded text-xs">关闭</button>
        </div>
      </div>
    </div>
    <!-- Compose -->
    <div v-if="showCompose" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50" @click.self="showCompose=false">
      <div class="glass-panel p-6 w-full max-w-lg mx-4 neon-border animate-slide-up">
        <h3 class="text-lg font-semibold mb-4">发送消息</h3>
        <form @submit.prevent="sendMessage" class="space-y-3">
          <select v-model="compose.receiver_id" required class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm">
            <option value="">选择收件人...</option>
            <option v-for="u in users" :key="u.id" :value="u.id">{{ u.name }} (@{{ u.username }})</option>
          </select>
          <input v-model="compose.subject" placeholder="主题" class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm focus:border-cockpit-gold outline-none transition-all" />
          <textarea v-model="compose.body" placeholder="消息内容" rows="4" required class="w-full px-3 py-2 bg-white/5 border border-cockpit-border/30 rounded-lg text-sm focus:border-cockpit-gold outline-none transition-all" />
          <div class="flex justify-end gap-3">
            <button type="button" @click="showCompose=false" class="px-4 py-2 rounded-lg text-sm text-cockpit-muted">取消</button>
            <button type="submit" class="px-4 py-2 bg-cockpit-accent rounded-lg text-sm">发送</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'; import api from '@/api/client'
const tab = ref('inbox'); const messages = ref<any[]>([]); const users = ref<any[]>([])
const detailMsg = ref<any>(null); const showCompose = ref(false)
const compose = ref({ receiver_id: '', subject: '', body: '' })
const avatarColor=(n:string)=>{const c=['#FF4D2E','#F97316','#FBBF24','#22C55E','#3B82F6','#8B5CF6','#EC4899'];return c[n?.charCodeAt(0)%c.length]||c[0]}
const formatTime=(t:string)=>{if(!t)return'';const d=new Date(t);return d.toLocaleDateString('zh-CN',{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'})}

async function loadMessages() {
  try { const r: any = await api.get(tab.value==='inbox'?'/messages/inbox':'/messages/sent'); messages.value = r.data?.items || [] } catch {}
}
onMounted(async () => { await loadMessages()
  try { const r: any = await api.get('/users'); users.value = r.data?.items || [] } catch {}
})

async function openMsg(m: any) {
  detailMsg.value = m
  if (!m.is_read && tab.value === 'inbox') {
    try { await api.put(`/messages/${m.id}/read`); m.is_read = true } catch {}
  }
}

function replyMsg() {
  showCompose.value = true
  compose.value = { receiver_id: String(detailMsg.value?.sender_id || ''), subject: 'Re: ' + (detailMsg.value?.subject || ''), body: '' }
  detailMsg.value = null
}

async function sendMessage() {
  if (!compose.value.receiver_id) return
  try {
    const r: any = await api.post('/messages', null, { params: compose.value })
    if (r.code === 200) { showCompose.value = false; compose.value = { receiver_id: '', subject: '', body: '' }; tab.value = 'sent'; await loadMessages() }
  } catch {}
}

watch(tab, () => loadMessages())
import { watch } from 'vue'
</script>
