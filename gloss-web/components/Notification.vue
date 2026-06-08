<template>
  <div
    aria-live="assertive"
    class="fixed inset-0 z-50 flex items-start pt-12 pointer-events-none"
  >
    <div class="flex flex-col items-center w-full space-y-4">
      <transition
        enter-active-class="transition duration-300 ease-out transform"
        enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
        enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
        leave-active-class="transition duration-100 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="show"
          class="overflow-hidden bg-white rounded-lg shadow-lg pointer-events-auto ring-1 ring-black ring-opacity-5"
        >
          <div class="p-4">
            <div class="flex items-start">
              <div class="flex-shrink-0">
                <CheckCircleIcon
                  v-if="isSuccess"
                  class="w-6 h-6 text-green-400"
                  aria-hidden="true"
                />
                <XCircleIcon
                  v-else
                  class="w-6 h-6 text-red-400"
                  aria-hidden="true"
                />
              </div>
              <div class="ml-3 flex-1 pt-0.5">
                <p class="text-sm font-medium text-gray-900">{{ text }}</p>
              </div>
              <div class="flex flex-shrink-0 ml-4"></div>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { CheckCircleIcon, XCircleIcon } from "@heroicons/vue/24/outline";

const props = defineProps({
  show: Boolean,
  text: String,
  isSuccess: Boolean,
});
</script>
