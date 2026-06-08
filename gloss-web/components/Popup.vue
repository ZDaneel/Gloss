<template>
  <div
    v-if="isVisible"
    ref="popup"
    class="fixed top-0 left-0 flex flex-col items-center p-4 space-y-4 rounded-lg shadow-xl bg-base-200"
    :class="{ 'w-82': withSwitch, 'w-60': !withSwitch }"
    v-on-click-outside="close"
    tabindex="0"
    @click.stop
    :style="{
      zIndex: 60,
      top: popupPosition.top + 'px',
      left: popupPosition.left + 'px',
    }"
  >
    <div class="w-full">
      <h3 class="text-sm font-semibold text-left text-base-content">
        {{ title }}
      </h3>
      <div class="flex items-center mt-1">
        <span class="text-xs">{{ titleExplanation }}</span>
      </div>
    </div>
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps } from "vue";
// @ts-ignore
import { vOnClickOutside } from "@vueuse/components";

const props = defineProps({
  title: String,
  titleExplanation: String,
  withSwitch: Boolean,
});

const popup = ref();
const isVisible = ref(false);
const popupPosition = ref({ top: 0, left: 0 });

const calculatePosition = (buttonRef: Ref<HTMLElement | null>) => {
  if (buttonRef.value) {
    const buttonRect = buttonRef.value.getBoundingClientRect();
    const leftOffset = props.withSwitch ? 140 : 100;
    popupPosition.value = {
      top: buttonRect.top - popup.value.offsetHeight - 12,
      left: buttonRect.left - leftOffset,
    };
  }
};

const toggle = async (buttonRef: Ref<HTMLElement | null>) => {
  isVisible.value = !isVisible.value;
  if (isVisible.value) {
    await nextTick();
    calculatePosition(buttonRef);
  }
};

defineExpose({ toggle });

const close = () => {
  setTimeout(() => {
    isVisible.value = false;
  }, 10);
};
</script>
