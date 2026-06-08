<template>
  <div>
    <div class="flex items-center justify-between space-x-3">
      <input
        type="range"
        :min="rangeMin"
        :max="rangeMax"
        :step="rangeStep"
        v-model.number="rangeValue"
        class="w-1/2 range range-primary range-sm"
        :disabled="isUnlimited"
      />
      <input
        type="number"
        :min="rangeMin"
        :max="rangeMax"
        :step="rangeStep"
        v-model.number="rangeValue"
        class="w-1/4 input input-sm input-primary disabled:border-gray-300"
        :disabled="isUnlimited"
      />
      <input
        type="checkbox"
        v-model="isUnlimited"
        class="toggle toggle-primary"
        @change="emitSwitchChange"
      />
      <span class="font-medium text-md whitespace-nowrap">
        {{ contextUnlimitedText }}</span
      >
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, watch } from "vue";
import { useI18n } from "vue-i18n";
const { t } = useI18n();
const contextUnlimitedText = computed(() => t("chat.contextUnlimited"));

const props = defineProps({
  rangeMin: Number,
  rangeMax: Number,
  rangeStep: Number,
  rangeValue: Number,
  isUnlimited: Boolean,
});

const emit = defineEmits(["update:rangeValue", "update:isUnlimited"]);

const rangeValue = ref(props.rangeValue);
const isUnlimited = ref(props.isUnlimited);

watch(rangeValue, (newValue) => {
  emit("update:rangeValue", newValue);
});

watch(isUnlimited, (newValue) => {
  emit("update:isUnlimited", newValue);
});

function emitSwitchChange() {
  emit("update:isUnlimited", isUnlimited.value);
}
</script>
