import SideBar from '../components/SideBar.vue';
<template>
  <div class="flex">
    <SideBar />
    <Drawer />
    <div :class="`flex-grow transition-all duration-300 ${isDrawerOpen ? 'ml-[24rem]' : ''}`">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import SideBar from '~/components/SideBar.vue';
import Drawer from '~/components/Drawer.vue';

import { useDrawerStore } from '@/store';

const drawerStore = useDrawerStore();
const isDrawerOpen = computed(() => drawerStore.isDrawerOpen);
</script>~/store/modules/drawer/drawer