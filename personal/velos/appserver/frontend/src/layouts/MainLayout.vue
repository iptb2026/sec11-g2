<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
        <q-toolbar>
          <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />

          <q-toolbar-title>
            <div class="text-h6">Velos</div>
            <div class="text-caption">Admin Console</div>
          </q-toolbar-title>

          <div class="row items-center">
            <q-input dense outlined placeholder="Search" class="q-mr-md" v-model="search" @keyup.enter="onSearch" />

            <q-badge :label="notifCount" color="red" align="top right" v-if="notifCount>0">
              <q-btn flat round icon="notifications" @click="openNotifications" />
            </q-badge>
            <q-btn flat round icon="notifications" v-if="notifCount===0" @click="openNotifications" />

            <q-btn flat round icon="logout" aria-label="Logout" @click="logout">
              <q-tooltip>Logout</q-tooltip>
            </q-btn>

            <q-menu v-model="notifOpen" anchor="bottom right" self="top right">
              <q-list style="min-width:320px">
                <q-item-label header>Notifications</q-item-label>
                <q-separator />
                <q-item v-for="n in notifications" :key="n.id" clickable @click="markRead(n)">
                  <q-item-section>
                    <div class="text-subtitle2">{{ n.title }}</div>
                    <div class="text-caption">{{ n.body }}</div>
                  </q-item-section>
                  <q-item-section side class="text-caption">{{ new Date(n.created_at).toLocaleString() }}</q-item-section>
                </q-item>
                <q-separator />
                <q-item clickable v-close-popup @click="goProfile"><q-item-section>Profile</q-item-section></q-item>
                <q-item clickable v-close-popup @click="logout"><q-item-section>Logout</q-item-section></q-item>
              </q-list>
            </q-menu>
          </div>
        </q-toolbar>
      </q-header>

      <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
        <q-list>
          <q-item-label header>Navigation</q-item-label>
          <q-item clickable v-if="can(['admin','staff'])" to="/admin/dashboard"><q-item-section>Dashboard</q-item-section></q-item>
          <q-item clickable v-if="can(['admin'])" to="/admin/users"><q-item-section>Users</q-item-section></q-item>
          <q-item clickable v-if="can(['staff','admin'])" to="/staff/customers"><q-item-section>Customers</q-item-section></q-item>
          <q-item clickable v-if="can(['customer'])" to="/customer/profile"><q-item-section>My Profile</q-item-section></q-item>
        </q-list>
      </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import notificationService from '@/services/notificationService'

const { can, logout: authLogout } = useAuth()
import { useQuasar } from 'quasar'
import { watch } from 'vue'
import { useRouter } from 'vue-router'

const $q = useQuasar()
const router = useRouter()
watch(() => router.currentRoute.value.fullPath, () => {
  if (!$q.screen.gt.sm) leftDrawerOpen.value = false
})
const linksList = [
  {
    label: 'Docs',
    caption: 'quasar.dev',
    icon: 'school',
    link: 'https://quasar.dev'
  },
  {
    label: 'GitHub',
    caption: 'github.com/quasarframework',
    icon: 'code',
    link: 'https://github.com/quasarframework'
  },
  {
    label: 'Discord Chat Channel',
    caption: 'chat.quasar.dev',
    icon: 'chat',
    link: 'https://chat.quasar.dev'
  },
  {
    label: 'Forum',
    caption: 'forum.quasar.dev',
    icon: 'record_voice_over',
    link: 'https://forum.quasar.dev'
  },
  {
    label: 'Twitter',
    caption: '@quasarframework',
    icon: 'rss_feed',
    link: 'https://twitter.quasar.dev'
  },
  {
    label: 'Facebook',
    caption: '@QuasarFramework',
    icon: 'public',
    link: 'https://facebook.quasar.dev'
  },
  {
    label: 'Quasar Awesome',
    caption: 'Community Quasar projects',
    icon: 'favorite',
    link: 'https://awesome.quasar.dev'
  }
]

const leftDrawerOpen = ref(false)
const search = ref('')
const notifOpen = ref(false)
const notifications = notificationService.list()
const notifCount = computed(() => notificationService.unreadCount())

function toggleLeftDrawer() { leftDrawerOpen.value = !leftDrawerOpen.value }
function onSearch() { if (search.value) console.log('search for', search.value) }
function openNotifications() { notifOpen.value = !notifOpen.value }
function goProfile() { window.location.hash = '#/customer/profile' }

function logout() { authLogout() }
function markRead(n) { notificationService.markRead(n.id) }
</script>
