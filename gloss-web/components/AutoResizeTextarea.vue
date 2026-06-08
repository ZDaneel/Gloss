<template>
  <div class="flex items-center">
    <textarea
      v-model="content"
      ref="textarea"
      :class="textareaClass"
      :style="{ height: textareaHeight + '!important' }"
      @input="adjustHeight"
      :placeholder="placeholder"
    ></textarea>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted } from "vue";

const props = defineProps({
  modelValue: {
    type: String,
    default: "",
  },
  placeholder: {
    type: String,
    default: "",
  },
  maxLines: {
    type: Number,
    default: 6,
  },
});

const emit = defineEmits(["update:modelValue"]);
const content = ref(props.modelValue);
const textareaHeight = ref("1rem");
const textarea = ref(null);

const textareaClass = computed(
  () =>
    "w-full p-2 pt-3 overflow-hidden text-xl resize-none rounded-2xl focus:outline-none bg-base-100"
);

watch(
  () => props.modelValue,
  (newValue) => {
    content.value = newValue;
    adjustHeight();
  }
);

watch(content, (newValue) => {
  emit("update:modelValue", newValue);
  adjustHeight();
});

onMounted(() => {
  adjustHeight();
});

const adjustHeight = () => {
  nextTick(() => {
    const el = textarea.value;
    if (!el) return;

    el.style.height = "auto";
    el.style.height = el.scrollHeight + "px";

    const lineHeight = parseFloat(getComputedStyle(el).lineHeight);
    const maxHeight = props.maxLines * lineHeight;

    if (el.scrollHeight > maxHeight) {
      el.style.height = `${maxHeight}px`;
      el.style.overflowY = "auto";
    } else {
      el.style.overflowY = "hidden";
    }

    textareaHeight.value = el.style.height;
  });
};

defineExpose({
  textarea,
});
</script>

<style scoped>
textarea {
  line-height: 1.5rem;
  font-size: 1rem;
}
</style>
