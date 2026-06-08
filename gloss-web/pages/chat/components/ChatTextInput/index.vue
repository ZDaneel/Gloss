<template>
  <div class="relative p-2 rounded-lg shadow-xl bg-base-100">
    <!-- 图标行 -->
    <ToolRow
      :show-tip="false"
      :temperature="localTemperature"
      :contextCount="localContextCount"
      :isContextUnlimited="localIsContextUnlimited"
      :paragraphCount="localParagraphCount"
      :tableEnhanceOpen="localTableEnhanceOpen"
      @update:temperature="updateTemperature"
      @update:contextCount="updateContextCount"
      @update:isContextUnlimited="updateIsContextUnlimited"
      @update:paragraphCount="updateParagraphCount"
      @update:tableEnhanceOpen="updateTableEnhanceOpen"
    />
    <!-- 输入文本区域 -->
    <div class="flex items-end">
      <div class="flex-grow">
        <AutoResizeTextarea v-model="localText" :placeholder="placeholder" />
      </div>
      <!-- 发送按钮 -->
      <div class="ml-4">
        <button
          v-if="!props.loading"
          @click="sendMessage"
          class="p-3 mb-3 text-white bg-blue-500 rounded-full hover:bg-blue-700"
        >
          <PaperAirplaneIcon class="w-5 h-5" />
        </button>
        <button v-else @click="handleStop" class="mb-1">
          <span
            class="text-blue-500 loading loading-spinner loading-lg hover:text-blue-700"
          ></span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineProps, defineEmits } from "vue";
import { PaperAirplaneIcon } from "@heroicons/vue/24/outline";
import AutoResizeTextarea from "~/components/AutoResizeTextarea.vue";
import { useI18n } from "vue-i18n";
import ToolRow from "@/components/ToolRow.vue";

const { t } = useI18n();
const placeholder = computed(() => t("textareaPlaceholder"));

const props = defineProps({
  modelValue: String,
  loading: Boolean,
  temperature: Number,
  paragraphCount: Number,
  contextCount: Number,
  isContextUnlimited: Boolean,
  tableEnhanceOpen: Boolean,
});

const emit = defineEmits([
  "update:modelValue",
  "handleSubmit",
  "handleStop",
  "update:temperature",
  "update:paragraphCount",
  "update:contextCount",
  "update:isContextUnlimited",
  "update:tableEnhanceOpen",
]);

const localText = ref(props.modelValue);

const localTemperature = ref(props.temperature);
const localParagraphCount = ref(props.paragraphCount);
const localContextCount = ref(props.contextCount);
const localIsContextUnlimited = ref(props.isContextUnlimited);
const localTableEnhanceOpen = ref(props.tableEnhanceOpen);

const updateTemperature = (value: number) => {
  localTemperature.value = value;
};

const updateParagraphCount = (value: number) => {
  localParagraphCount.value = value;
};

const updateContextCount = (value: number) => {
  localContextCount.value = value;
};

const updateIsContextUnlimited = (value: boolean) => {
  localIsContextUnlimited.value = value;
};

const updateTableEnhanceOpen = (value: boolean) => {
  localTableEnhanceOpen.value = value;
};

watch(
  () => props.modelValue,
  (newValue) => {
    localText.value = newValue;
  }
);

watch(localText, (newValue) => {
  emit("update:modelValue", newValue);
});

watch(localTemperature, (newValue) => {
  emit("update:temperature", newValue);
});

watch(localParagraphCount, (newValue) => {
  emit("update:paragraphCount", newValue);
});

watch(localContextCount, (newValue) => {
  emit("update:contextCount", newValue);
});

watch(localIsContextUnlimited, (newValue) => {
  emit("update:isContextUnlimited", newValue);
});

watch(localTableEnhanceOpen, (newValue) => {
  emit("update:tableEnhanceOpen", newValue);
});

const sendMessage = () => {
  emit("handleSubmit");
};

const handleStop = () => {
  emit("handleStop");
};
</script>
