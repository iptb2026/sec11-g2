<template>
  <div class="profile-photo-editor">
    <button type="button" class="profile-photo-trigger" aria-label="Change profile picture" title="Change profile picture" @click="openEditor">
      <ProfileAvatar :size="size" />
      <span class="profile-camera-badge" aria-hidden="true"><q-icon name="photo_camera" /></span>
    </button>
    <q-dialog v-model="open" position="bottom" :persistent="busy || preparing">
      <q-card class="profile-photo-sheet" aria-label="Change profile picture">
        <div class="photo-sheet-handle" aria-hidden="true" />
        <div class="photo-sheet-preview">
          <q-avatar size="76px"><img v-if="preview || auth.profilePhoto" :src="preview || auth.profilePhoto" alt="Profile picture preview" style="object-fit:cover" /><ProfileAvatar v-else size="76px" /></q-avatar>
        </div>
        <q-separator />
        <input ref="libraryInput" class="photo-file-input" type="file" accept="image/jpeg,image/png,image/webp" aria-label="Choose from library" @change="selectedFile" />
        <input ref="cameraInput" class="photo-file-input" type="file" accept="image/*" capture="user" aria-label="Take photo" @change="selectedFile" />
        <div v-if="pendingCamera && preview" class="photo-confirm-actions">
          <p>Use this photo as your profile picture?</p>
          <div><q-btn flat label="Retake" :disable="busy" @click="startCamera" /><q-btn color="primary" label="Use photo" :loading="busy" @click="save" /></div>
        </div>
        <div v-else class="photo-sheet-actions">
          <button type="button" :disabled="busy || preparing" @click="libraryInput.click()"><q-icon name="image" /><span>Choose from library</span></button>
          <button type="button" :disabled="busy || preparing" @click="startCamera"><q-icon name="photo_camera" /><span>Take photo</span></button>
          <button v-if="auth.profilePhoto" type="button" class="photo-remove-action" :disabled="busy || preparing" @click="remove"><q-icon name="delete_outline" /><span>Remove current picture</span></button>
        </div>
        <div v-if="busy || preparing" class="photo-sheet-status" role="status"><q-spinner size="20px" /><span>{{ preparing ? 'Preparing photo…' : 'Updating photo…' }}</span></div>
        <div v-if="error" class="photo-sheet-error"><q-banner class="bank-feedback" role="alert">{{ error }}</q-banner><q-btn v-if="preview" flat label="Try again" :disable="busy || preparing" @click="save" /></div>
      </q-card>
    </q-dialog>
    <q-dialog v-model="cameraOpen" position="bottom" maximized @hide="stopCamera">
      <q-card class="camera-capture-sheet">
        <div class="photo-sheet-handle" aria-hidden="true" />
        <div class="camera-capture-header"><q-btn flat round icon="close" aria-label="Close camera" @click="cameraOpen = false" /><strong>Take photo</strong><span /></div>
        <div class="camera-preview-frame"><video ref="video" autoplay muted playsinline aria-label="Camera preview" /><div class="camera-frame" aria-hidden="true"><i /><i /><i /><i /></div><p v-if="cameraError" class="camera-error">{{ cameraError }}</p></div>
        <div class="camera-capture-actions"><q-btn flat label="Cancel" @click="cameraOpen = false" /><q-btn round color="white" text-color="dark" icon="camera" aria-label="Capture photo" :disable="!!cameraError" @click="capturePhoto" /></div>
      </q-card>
    </q-dialog>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import { useAuthStore } from '@/stores/auth-store'
import api from '@/services/api'
import ProfileAvatar from '@/components/ProfileAvatar.vue'
defineProps({ size: { type: String, default: '58px' } })
const auth = useAuthStore(), $q = useQuasar()
const open = ref(false), preview = ref(''), error = ref(''), busy = ref(false), preparing = ref(false), pendingCamera = ref(false), cameraOpen = ref(false), cameraError = ref(''), video = ref(null)
const libraryInput = ref(null), cameraInput = ref(null)
let cameraStream = null
let selection = 0
function openEditor () { selection++; preview.value = ''; error.value = ''; open.value = true }
function selectedFile (event) { const file = event.target.files?.[0]; event.target.value = ''; if (file) choose(file) }
async function choose (chosen) {
  const current = ++selection
  preview.value = ''; error.value = ''
  if (!chosen) return
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(chosen.type) || chosen.size > 5 * 1024 * 1024) { error.value = 'Choose a JPG, PNG, or WebP smaller than 5 MB.'; return }
  preparing.value = true
  const url = URL.createObjectURL(chosen)
  try {
    const image = new Image(); image.src = url; await image.decode()
    const canvas = document.createElement('canvas'); canvas.width = canvas.height = 256
    const context = canvas.getContext('2d'), side = Math.min(image.naturalWidth, image.naturalHeight)
    context.fillStyle = '#ffffff'; context.fillRect(0, 0, 256, 256)
    context.drawImage(image, (image.naturalWidth - side) / 2, (image.naturalHeight - side) / 2, side, side, 0, 0, 256, 256)
    if (current === selection) { preview.value = canvas.toDataURL('image/jpeg', 0.85); preparing.value = false; pendingCamera.value = false; await save() }
  } catch { if (current === selection) error.value = 'This image could not be opened. Choose another photo.' }
  finally { URL.revokeObjectURL(url); preparing.value = false }
}
async function startCamera () {
  pendingCamera.value = true; cameraError.value = ''; cameraOpen.value = true
  try {
    if (!navigator.mediaDevices?.getUserMedia) throw new Error('Camera access is unavailable on this device.')
    cameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: { ideal: 1080 }, height: { ideal: 1080 } }, audio: false })
    await new Promise(resolve => requestAnimationFrame(resolve))
    if (video.value) { video.value.srcObject = cameraStream; await video.value.play() }
  } catch (e) {
    stopCamera(); cameraOpen.value = true
    cameraError.value = e.name === 'NotAllowedError' ? 'Camera permission was denied. Allow camera access and try again.' : e.message || 'Could not open the camera.'
  }
}
function stopCamera () { cameraStream?.getTracks().forEach(track => track.stop()); cameraStream = null; if (video.value) video.value.srcObject = null }
function capturePhoto () {
  const source = video.value
  if (!source?.videoWidth) return
  const side = Math.min(source.videoWidth, source.videoHeight), canvas = document.createElement('canvas'); canvas.width = canvas.height = 256
  const context = canvas.getContext('2d'); context.drawImage(source, (source.videoWidth - side) / 2, (source.videoHeight - side) / 2, side, side, 0, 0, 256, 256)
  preview.value = canvas.toDataURL('image/jpeg', 0.85); cameraOpen.value = false; stopCamera()
}
async function save () {
  busy.value = true; error.value = ''
  try { const { data } = await api.put('/auth/profile-photo', { image: preview.value }); auth.profilePhoto = data.profile_photo; open.value = false; $q.notify({ type: 'positive', message: 'Profile picture updated' }) }
  catch (e) { error.value = e.response?.status === 404 ? 'Photo uploads are temporarily unavailable. Please try again shortly.' : e.response?.data?.detail || 'Could not save your photo. Please try again.' }
  finally { busy.value = false }
}
async function remove () {
  busy.value = true; error.value = ''
  try { await api.delete('/auth/profile-photo'); auth.profilePhoto = null; open.value = false; $q.notify({ type: 'positive', message: 'Profile picture removed' }) }
  catch { error.value = 'Could not remove your photo. Please try again.' }
  finally { busy.value = false }
}
</script>
<style scoped>
.profile-photo-editor { display: inline-flex; flex: 0 0 auto; }
.profile-photo-trigger { position: relative; display: inline-flex; padding: 0; border: 2px solid #31577e; border-radius: 50%; background: transparent; cursor: pointer; }
.profile-photo-trigger:hover { border-color: #79b8ff; }
.profile-photo-trigger:focus-visible { outline: 3px solid #79b8ff; outline-offset: 4px; }
.profile-camera-badge { position: absolute; top: -4px; left: -4px; width: 23px; height: 23px; display: grid; place-items: center; border: 2px solid #080f1b; border-radius: 50%; color: white; background: #3478ff; pointer-events: none; }
.profile-camera-badge .q-icon { font-size: 13px; }
.profile-photo-sheet { width: 480px; max-width: 100vw !important; margin: 0; border-radius: 28px 28px 0 0 !important; background: #171c1f; color: #f5f5f5; padding-bottom: calc(20px + env(safe-area-inset-bottom)); }
.photo-sheet-handle { width: 48px; height: 4px; margin: 16px auto 0; background: #9da3ae; border-radius: 4px; }
.photo-sheet-preview { display: flex; justify-content: center; padding: 28px 20px 24px; }
.photo-file-input { display: none; }
.photo-sheet-actions { display: grid; padding: 12px 0; }
.photo-sheet-actions button { display: flex; align-items: center; gap: 20px; width: 100%; min-height: 76px; padding: 16px 26px; background: transparent; color: inherit; border: 0; text-align: left; font-size: 18px; line-height: 1.4; cursor: pointer; }
.photo-sheet-actions button .q-icon { font-size: 30px; flex: 0 0 30px; }
.photo-sheet-actions button:hover { background: #ffffff08; }
.photo-sheet-actions button:focus-visible { outline: 2px solid #79b8ff; outline-offset: -4px; }
.photo-sheet-actions button:disabled { opacity: .45; cursor: wait; }
.photo-sheet-actions .photo-remove-action { color: #ff334b; }
.photo-sheet-status { display: flex; align-items: center; justify-content: center; gap: 10px; padding: 8px 20px; font-size: 13px; }
.photo-sheet-error { padding: 0 20px 12px; }
.photo-confirm-actions { padding: 18px 20px 22px; text-align: center; }
.photo-confirm-actions p { margin: 0 0 14px; color: #dbe7f7; font-size: 15px; }
.photo-confirm-actions > div { display: flex; justify-content: center; gap: 10px; }
.camera-capture-sheet { display: flex; flex-direction: column; width: 100vw; min-height: 100dvh; background: #060d15; color: white; }
.camera-capture-header { display: grid; grid-template-columns: 48px 1fr 48px; align-items: center; padding: 12px 16px; text-align: center; }
.camera-preview-frame { position: relative; display: grid; flex: 1; min-height: 0; place-items: center; overflow: hidden; background: #02070b; }
.camera-preview-frame video { width: 100%; height: 100%; object-fit: cover; }
.camera-frame { position: absolute; width: min(72vw, 300px); aspect-ratio: 1; top: 50%; left: 50%; transform: translate(-50%, -50%); }
.camera-frame i { position: absolute; width: 36px; height: 36px; border: solid #55bfff; border-width: 0; }
.camera-frame i:nth-child(1) { top: 0; left: 0; border-top-width: 4px; border-left-width: 4px; border-radius: 12px 0 0; }
.camera-frame i:nth-child(2) { top: 0; right: 0; border-top-width: 4px; border-right-width: 4px; border-radius: 0 12px 0 0; }
.camera-frame i:nth-child(3) { bottom: 0; left: 0; border-bottom-width: 4px; border-left-width: 4px; border-radius: 0 0 0 12px; }
.camera-frame i:nth-child(4) { right: 0; bottom: 0; border-right-width: 4px; border-bottom-width: 4px; border-radius: 0 0 12px 0; }
.camera-error { position: absolute; inset: auto 24px 24px; padding: 12px; border-radius: 10px; background: #321e2a; color: #ffc5d0; text-align: center; }
.camera-capture-actions { display: flex; align-items: center; justify-content: space-between; min-height: 96px; padding: 14px 24px calc(14px + env(safe-area-inset-bottom)); }
.camera-capture-actions .q-btn[aria-label="Capture photo"] { width: 66px; height: 66px; border: 4px solid #a7b3c3; }
@media (max-width: 480px) { .profile-photo-sheet { width: 100vw; } .photo-sheet-actions button { padding-inline: 22px; font-size: 17px; } }
</style>
