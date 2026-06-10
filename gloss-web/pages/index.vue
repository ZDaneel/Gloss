<template>
  <div class="flex flex-col items-center justify-center min-h-screen px-4 bg-base-300">
    <h1 class="mb-8 text-5xl font-bold">{{ appName }}</h1>
    <div class="w-full max-w-3xl space-y-3">
      <!-- 原文粘贴区 -->
      <div class="rounded-lg shadow-xl bg-base-100">
        <textarea
          v-model="sourceText"
          class="w-full p-4 rounded-lg bg-base-100 resize-none focus:outline-none text-sm leading-relaxed"
          :placeholder="sourcePlaceholder"
          rows="10"
        />
      </div>
      <!-- 问题输入区 -->
      <div class="p-2 rounded-lg shadow-xl bg-base-100">
        <div class="pb-1">
          <AutoResizeTextarea
            ref="questionInputRef"
            v-model="question"
            :placeholder="questionPlaceholder"
            @keypress="handleEnter"
          />
        </div>
        <div class="flex items-center justify-between pt-3 pb-2 border-t border-base-300">
          <div class="flex items-center">
            <ToolRow
              class="p-1"
              :show-tip="true"
              :temperature="localTemperature"
              :contextCount="localContextCount"
              :isContextUnlimited="localIsContextUnlimited"
              :paragraphCount="localParagraphCount"
              :tableEnhanceOpen="localTableEnhanceOpen"
              @update:temperature="localTemperature = $event"
              @update:contextCount="localContextCount = $event"
              @update:isContextUnlimited="localIsContextUnlimited = $event"
              @update:paragraphCount="localParagraphCount = $event"
              @update:tableEnhanceOpen="localTableEnhanceOpen = $event"
            />
          </div>
          <button
            @click="sendMessage"
            :disabled="isLoading"
            class="btn btn-primary btn-sm"
          >
            <span v-if="isLoading" class="loading loading-spinner loading-xs mr-1" />
            {{ startReading }}
          </button>
        </div>
      </div>
    </div>
  </div>
  <Notification
    :show="notification_show"
    :text="notification_text"
    :isSuccess="notification_isSuccess"
  />
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import AutoResizeTextarea from "~/components/AutoResizeTextarea.vue";
import ToolRow from "@/components/ToolRow.vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();
const appName = computed(() => t("home.appName"));
const sourcePlaceholder = computed(() => t("home.sourcePlaceholder"));
const questionPlaceholder = computed(() => t("home.questionPlaceholder"));
const startReading = computed(() => t("home.startReading"));

import { useChatStore } from "@/store";
const chatStore = useChatStore();
const router = useRouter();
chatStore.initRouter(router);

const histories = computed(() =>
  chatStore.history.sort(
    (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
  )
);
const lastHistory = computed(() => histories.value[0]);
const localTemperature = ref(lastHistory.value?.temperature ?? 0.6);
const localContextCount = ref(lastHistory.value?.contextNum ?? 0);
const localParagraphCount = ref(lastHistory.value?.paragraphNum ?? 5);
const localIsContextUnlimited = ref(lastHistory.value?.isContextUnlimited ?? true);
const localTableEnhanceOpen = ref(lastHistory.value?.tableEnhanceOpen ?? false);

const sourceText = ref("");
const question = ref("");
const questionInputRef = ref<HTMLElement | null>(null);
const isLoading = ref(false);

const notification_show = ref(false);
const notification_text = ref("");
const notification_isSuccess = ref(true);

const showNotification = (message: string, isSuccess: boolean) => {
  notification_show.value = true;
  notification_text.value = message;
  notification_isSuccess.value = isSuccess;
  setTimeout(() => {
    notification_show.value = false;
  }, 2000);
};

const handleEnter = (event: KeyboardEvent) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
};

const sendMessage = () => {
  if (isLoading.value) return;
  if (sourceText.value.trim() === "") {
    showNotification(t("home.emptySource"), false);
    return;
  }
  if (question.value.trim() === "") {
    showNotification(t("home.emptyContent"), false);
    return;
  }

  const my_uuid = Date.now();
  const chat_id = my_uuid + 1;

  chatStore.addHistory({
    title: t("chat.newChatTitle"),
    isEdit: false,
    uuid: my_uuid,
    isFirst: true,
    updatedAt: new Date().toISOString(),
    temperature: localTemperature.value,
    contextNum: localContextCount.value,
    paragraphNum: localParagraphCount.value,
    isContextUnlimited: localIsContextUnlimited.value,
    tableEnhanceOpen: localTableEnhanceOpen.value,
    sourceText: sourceText.value,
  });

  chatStore.addChatByUuid(my_uuid, {
    chat_id,
    text: question.value,
    paragraphs: [],
    dateTime: new Date().toISOString(),
    isUser: true,
    error: false,
    requestOptions: { prompt: question.value },
  });

  router.push(`/chat/${my_uuid}`);
  sourceText.value = "";
  question.value = "";
};
</script>

<style></style>
