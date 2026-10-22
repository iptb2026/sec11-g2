<template>
  <q-dialog no-route-dismiss :maximized="$q.screen.width <= 700" :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" @hide="stop">
    <q-card class="scanner-dialog" style="width:460px;max-width:95vw">
      <q-card-section><div class="row items-center justify-between"><h2 class="section-heading">Scan QR code</h2><q-btn flat round icon="close" aria-label="Close scanner" v-close-popup /></div><p class="page-subtitle">Scan a Bembank receive code. You will review the recipient and amount before sending.</p></q-card-section>
      <q-card-section class="q-gutter-md">
        <q-banner v-if="error" class="bank-feedback" role="alert">{{ error }}</q-banner>
        <div class="scanner-viewfinder" :class="{ 'is-active': active }">
          <video ref="video" v-show="active" autoplay muted playsinline class="scanner-preview" />
          <div class="scanner-target" aria-hidden="true"><i /><i /><i /><i /></div>
          <p v-if="!active" class="scanner-placeholder">Position the QR code inside the frame</p>
        </div>
        <q-btn v-if="!active" outline icon="photo_camera" label="Start camera" :loading="starting" @click="start" />
        <div v-else class="row q-gutter-sm"><q-btn outline label="Stop camera" @click="stop" /><q-btn v-if="torchAvailable" outline icon="flash_on" :label="torch ? 'Turn flash off' : 'Turn flash on'" @click="toggleTorch" /></div>
        <q-file filled accept="image/png,image/jpeg,image/webp" label="Upload a QR image" :model-value="file" @update:model-value="readImage"><template #prepend><q-icon name="image" /></template></q-file>
        <p class="page-subtitle">Camera access needs HTTPS or localhost and your permission. Image upload works without camera access.</p>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>
<script setup>
import { ref, watch, nextTick, onBeforeUnmount } from 'vue'
import jsQR from 'jsqr'
import { parseBankQr } from '@/utils/bank-qr'
const props = defineProps({ modelValue: Boolean })
const emit = defineEmits(['update:modelValue', 'scanned'])
const video = ref(null), active = ref(false), starting = ref(false), error = ref(''), file = ref(null), torch = ref(false), torchAvailable = ref(false)
let stream, timer, generation = 0
function stop () { generation++; clearTimeout(timer); stream?.getTracks().forEach(track => track.stop()); stream = null; active.value = false; starting.value = false; torch.value = false; torchAvailable.value = false }
function accept (data) { const result = parseBankQr(data); stop(); emit('scanned', result); emit('update:modelValue', false) }
function decode (source, width, height) { const scale = Math.min(1, 1600 / Math.max(width, height)); const canvas = document.createElement('canvas'); canvas.width = Math.round(width * scale); canvas.height = Math.round(height * scale); const ctx = canvas.getContext('2d', { willReadFrequently: true }); ctx.drawImage(source, 0, 0, canvas.width, canvas.height); const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height); return jsQR(pixels.data, pixels.width, pixels.height)?.data }
async function start () {
  stop(); error.value = ''; starting.value = true; const current = generation
  try {
    if (!navigator.mediaDevices?.getUserMedia) throw new Error('Camera access is unavailable here. Upload a QR image instead.')
    const acquired = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false })
    if (current !== generation || !props.modelValue) { acquired.getTracks().forEach(t => t.stop()); return }
    stream = acquired; active.value = true; await nextTick(); video.value.srcObject = stream; await video.value.play()
    torchAvailable.value = !!stream.getVideoTracks()[0]?.getCapabilities?.().torch
    const tick = () => {
      if (current !== generation || !active.value) return
      if (video.value?.readyState >= 2) { try { const data = decode(video.value, video.value.videoWidth, video.value.videoHeight); if (data) { accept(data); return } } catch (e) { error.value = e.message || 'Could not read this QR code.' } }
      timer = setTimeout(tick, 180)
    }; tick()
  } catch (e) { if (current === generation) { stop(); error.value = e.name === 'NotAllowedError' ? 'Camera permission was denied. Allow access or upload an image.' : e.message || 'Could not start the camera.' } }
  finally { if (current === generation) starting.value = false }
}
async function readImage (selected) {
  stop(); file.value = selected; error.value = ''; if (!selected) return
  if (selected.size > 10 * 1024 * 1024) { error.value = 'Choose an image smaller than 10 MB.'; return }
  const current = generation, url = URL.createObjectURL(selected)
  try { const img = new Image(); img.src = url; await img.decode(); if (current !== generation || !props.modelValue) return; const data = decode(img, img.naturalWidth, img.naturalHeight); if (!data) throw new Error('No QR code found. Choose a clear image with the entire code visible.'); accept(data) } catch (e) { if (current === generation) error.value = e.message || 'Could not read this image.' } finally { URL.revokeObjectURL(url) }
}
async function toggleTorch () { try { await stream.getVideoTracks()[0].applyConstraints({ advanced: [{ torch: !torch.value }] }); torch.value = !torch.value } catch { error.value = 'Flash is not available on this camera.' } }
watch(() => props.modelValue, value => { if (!value) stop(); else { error.value = ''; file.value = null } })
onBeforeUnmount(stop)
</script>
<style scoped>.scanner-preview { display: block; width: 100%; max-height: 320px; object-fit: cover; border-radius: 12px; background: #080f1b; }</style>
