<template>
    <div
      :class="[
        'flex items-center p-2 rounded',
        type === 'link' ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' : 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300'
      ]"
    >
      <span class="mr-2">{{ content }}</span>
      <!-- <button @click="remove" class="text-red-500 dark:text-red-300">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          class="w-5 h-5"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button> -->
    </div>
  </template>
  
  <script setup>
  import { defineProps, defineEmits } from 'vue';
  
  const props = defineProps({
    content: String,
    type: {
      type: String,
      default: 'link'
    }
  });
  
  const emits = defineEmits(['remove']);
  
  const remove = () => {
    emits('remove');
  };
  </script>