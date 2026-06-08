<template>
  <div
    v-if="isVisible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
  >
    <div class="w-2/3 max-w-lg p-10 shadow-2xl rounded-3xl bg-base-100">
      <h2 class="mb-6 text-3xl font-bold">{{ $t("deleteModal.title") }}</h2>
      <p class="mb-8 text-lg">
        {{ $t("deleteModal.contentPrefix") }}
        <span class="text-xl font-bold">{{ title }}</span>
        {{ $t("deleteModal.contentSuffix") }}
      </p>

      <div class="flex justify-end space-x-4">
        <button @click="close" class="btn btn-md">
          {{ $t("deleteModal.cancelText") }}
        </button>
        <button @click="confirmDelete" class="btn btn-md btn-error">
          {{ $t("deleteModal.confirmText") }}
        </button>
      </div>
    </div>
  </div>
</template>




<script setup>
import { defineProps, defineEmits } from "vue";

const props = defineProps({
  isVisible: Boolean,
  title: String,
  uuid: Number,
});

const emit = defineEmits(["close", "confirmDelete"]);

const close = () => {
  emit("close");
};

const confirmDelete = () => {
  emit("confirmDelete", props.uuid);
};
</script>
