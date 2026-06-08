import SideBar from '../components/SideBar.vue';
<template>
  <div class="flex">
    <SideBar />
    <div class="flex-grow">
      <slot />
    </div>
  </div>
</template>

<script setup>
import SideBar from '~/components/SideBar.vue';
</script>