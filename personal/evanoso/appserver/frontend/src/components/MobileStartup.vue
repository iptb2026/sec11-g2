<template>
  <div :inert="visible || undefined" :aria-hidden="visible ? 'true' : undefined">
    <slot />
  </div>
  <Transition name="startup-fade">
    <div v-if="visible" class="mobile-startup" role="status" aria-label="Opening Bembank">
      <div class="startup-lockup" aria-hidden="true">
        <div class="startup-mark">
          <BankLogo class="startup-piece startup-piece-top" />
          <BankLogo class="startup-piece startup-piece-middle" />
          <BankLogo class="startup-piece startup-piece-bottom" />
        </div>
        <div class="startup-wordmark"><span>bembank.</span></div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import BankLogo from '@/components/BankLogo.vue'

const visible = ref(true)
let timer
let wasHidden = false

function start () {
  clearTimeout(timer)
  visible.value = true
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  // A fixed duration keeps the animation independent of API/network availability.
  timer = setTimeout(() => { visible.value = false }, reducedMotion ? 200 : 1300)
}
function onVisibilityChange () {
  if (document.hidden) {
    wasHidden = true
    clearTimeout(timer)
    visible.value = false
  } else if (wasHidden) {
    wasHidden = false
    start()
  }
}
onMounted(() => {
  start()
  // Web/PWA tabs and the mobile WebView report foreground changes here.
  document.addEventListener('visibilitychange', onVisibilityChange)
})
onBeforeUnmount(() => {
  clearTimeout(timer)
  document.removeEventListener('visibilitychange', onVisibilityChange)
})
</script>

<style scoped>
.mobile-startup {
  position: fixed;
  inset: 0;
  z-index: 100000;
  display: grid;
  place-items: center;
  overflow: hidden;
  touch-action: none;
  background: #080f19;
  color: #f4f7ff;
  padding: env(safe-area-inset-top) 24px env(safe-area-inset-bottom);
}
/* Three cuts of the actual bank mark slot together, then make room for its name. */
.startup-lockup { position: relative; width: 250px; height: 76px; }
.startup-mark {
  position: absolute;
  inset: 0 auto 0 0;
  width: 76px;
  color: #168aff;
  animation: mark-settle 1s cubic-bezier(.22, 1, .36, 1) both;
}
.startup-piece { position: absolute; inset: 0; width: 76px; height: 76px; }
.startup-piece-top {
  clip-path: inset(0 0 55% 0);
  animation: cut-from-left .45s .05s cubic-bezier(.16, 1, .3, 1) both;
}
.startup-piece-middle {
  clip-path: inset(45% 0 40% 0);
  animation: cut-from-right .4s .1s cubic-bezier(.16, 1, .3, 1) both;
}
.startup-piece-bottom {
  clip-path: inset(60% 0 0 0);
  animation: cut-from-left .45s .15s cubic-bezier(.16, 1, .3, 1) both;
}
.startup-wordmark {
  position: absolute;
  left: 90px;
  top: 18px;
  overflow: hidden;
  font-family: 'Manrope', sans-serif;
  font-weight: 800;
  font-size: 30px;
  line-height: 40px;
  letter-spacing: -1.2px;
}
.startup-wordmark span {
  display: block;
  animation: name-reveal .35s .65s cubic-bezier(.22, 1, .36, 1) both;
}
.startup-fade-leave-active { transition: opacity .18s ease-out; }
.startup-fade-leave-to { opacity: 0; }
@keyframes cut-from-left {
  from { opacity: 0; transform: translateX(-24px); }
  to { opacity: 1; transform: translateX(0); }
}
@keyframes cut-from-right {
  from { opacity: 0; transform: translateX(24px); }
  to { opacity: 1; transform: translateX(0); }
}
@keyframes mark-settle {
  0%, 45% { transform: translateX(87px); }
  100% { transform: translateX(0); }
}
@keyframes name-reveal {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}
@media (prefers-reduced-motion: reduce) {
  .startup-mark, .startup-piece, .startup-wordmark span { animation: none; }
  .startup-fade-leave-active { transition: none; }
}
</style>
