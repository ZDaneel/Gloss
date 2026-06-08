<template>
  <div
    v-if="isVisible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
  >
    <div class="w-full max-w-3xl p-4 rounded shadow-lg bg-base-200">
      <!-- 标题和关闭按钮 -->
      <div class="flex items-center justify-between">
        <h2 class="flex-grow text-lg font-bold text-center">{{ title }}</h2>
        <button @click="closeModal" class="ml-auto text-gray-500">
          <Icon name="ic:baseline-close" class="w-5 h-5 text-gray-500" />
        </button>
      </div>
      <div class="mt-3 overflow-auto max-h-[500px]">
        <div
          v-if="!imageLoaded"
          class="flex items-center justify-center w-full h-full"
        >
          <span class="loading loading-spinner loading-lg"></span>
        </div>
        <img
          v-show="imageLoaded"
          :src="props.screenshotDataUrl"
          alt="Screenshot"
          class="w-full h-auto"
          @load="handleImageLoad"
        />
      </div>
      <button @click="downloadImage" class="w-full mt-4 btn btn-info" :disabled="!imageLoaded">
        {{ downloadText }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from "vue";
import { useI18n } from "vue-i18n";
const { t } = useI18n();
const title = t("chat.screenshotModal.title");
const downloadText = t("chat.screenshotModal.download");

const imageLoaded = ref(false);
const handleImageLoad = () => {
  imageLoaded.value = true;
};

const props = defineProps({
  isVisible: Boolean,
  screenshotDataUrl: String,
});

const emits = defineEmits(["close"]);

const closeModal = () => {
  emits("close");
};

const downloadImage = () => {
  const tempLink = document.createElement("a");
  tempLink.style.display = "none";
  if (props.screenshotDataUrl === undefined) {
    return;
  }

  tempLink.href = props.screenshotDataUrl;

  tempLink.setAttribute("download", "screenshot.png");
  document.body.appendChild(tempLink);
  tempLink.click();
  document.body.removeChild(tempLink);
};

watch(() => props.isVisible, (newValue) => {
  if (newValue) {
    imageLoaded.value = false;
  }
});
</script>
