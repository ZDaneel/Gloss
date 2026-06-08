<template>
  <div
    class="flex flex-col items-center justify-center min-h-screen px-4 bg-base-300"
  >
    <h1 class="mb-8 text-5xl font-bold">{{ appName }}</h1>
    <div class="w-full max-w-3xl">
      <div class="p-2 rounded-lg shadow-xl bg-base-100">
        <!-- 输入文本区域 -->
        <div class="pb-1">
          <AutoResizeTextarea
            ref="textInputRef"
            v-model="textInput"
            :placeholder="placeholder"
            @keypress="handleEnter"
          />
        </div>
        <!-- 工具栏 -->
        <div
          class="flex items-start justify-between pt-3 pb-2 border-t border-base-300"
        >
          <!-- 左侧链接或文件信息 -->
          <div class="flex flex-wrap items-centerspace-x-2">
            <Tag
              v-for="(item, index) in tags"
              class="mx-1 my-2"
              :key="index"
              :content="item.content"
              :type="item.type"
              @remove="removeTag(index)"
            />
            <!-- 加载图标 -->
            <div v-if="isLoading" class="flex items-center justify-center">
              <span class="loading loading-dots loading-md"></span>
            </div>
          </div>
          <!-- 右侧图标 -->
          <div class="flex items-center space-x-1">
            <ToolRow
              class="p-1"
              :show-tip="true"
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
            <div class="divider divider-horizontal" />
            <button
              @click="toggleLinkInput"
              :class="[
                'p-1 tooltip tooltip-bottom rounded-lg btn btn-ghost btn-sm',
                isLoading || isTagsFull
                  ? 'cursor-not-allowed text-gray-500'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-neutral-content',
              ]"
              :data-tip="toolbarLinkTip"
              :disabled="isLoading || isTagsFull"
            >
              <LinkIcon class="w-6 h-6" />
            </button>
            <button
              @click="sendMessage"
              class="p-1 text-blue-500 hover:text-blue-700"
              :disabled="sendDisabled || isLoading"
            >
              <PaperAirplaneIcon class="w-6 h-6" />
            </button>
          </div>
        </div>
        <!-- 链接输入框 -->
        <div v-if="showLinkInput" class="mt-3">
          <div class="flex items-center space-x-2">
            <input
              ref="linkInputRef"
              v-model="newLink"
              type="text"
              class="flex-1 p-2 rounded bg-base-100 focus:outline-none"
              :placeholder="linkPlaceholder"
              :disabled="isLoading"
              @keyup.enter="addLink"
            />
            <div class="text-sm text-gray-500">
              {{ confirmTextPrefix }}
              <button
                class="ml-1 kbd btn btn-sm btn-outline"
                @mousedown="addLink"
              >
                Enter
              </button>
              {{ confirmTextSuffix }}
            </div>
          </div>
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
import { ref } from "vue";
import {
  LinkIcon,
  DocumentPlusIcon,
  PaperAirplaneIcon,
} from "@heroicons/vue/24/outline";
import { uploadPDF, removePDF, uploadLink, removeLink } from "@/api";
import Tag from "~/components/Tag.vue";
import AutoResizeTextarea from "~/components/AutoResizeTextarea.vue";
import ToolRow from "@/components/ToolRow.vue";
import { useI18n } from "vue-i18n";
const { t } = useI18n();
const appName = computed(() => t("home.appName"));
const placeholder = computed(() => t("textareaPlaceholder"));
const toolbarLinkTip = computed(() => t("toolbar.linkTip"));
const toolbarUploadTip = computed(() => t("toolbar.uploadTip"));
const linkPlaceholder = computed(() => t("toolbar.placeholder"));
const confirmTextPrefix = computed(() => t("toolbar.confirmTextPrefix"));
const confirmTextSuffix = computed(() => t("toolbar.confirmTextSuffix"));
const emptyContentText = computed(() => t("home.emptyContent"));
const emptyTagsText = computed(() => t("home.emptyTags"));
import { useChatStore } from "@/store";
const chatStore = useChatStore();
const router = useRouter();
chatStore.initRouter(router);

const histories = computed(() => {
  return chatStore.history.sort((a, b) => {
    return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
  });
});
const lastHistory = computed(() => histories.value[0]);
const temperatureValue = lastHistory.value?.temperature ?? 0.6;
const localTemperature = ref(temperatureValue);
const contextCountValue = lastHistory.value?.contextNum ?? 0;
const localContextCount = ref(contextCountValue);
const paragraphCountValue = lastHistory.value?.paragraphNum ?? 5;
const localParagraphCount = ref(paragraphCountValue);
const isContextUnlimitedValue = lastHistory.value?.isContextUnlimited ?? true;
const localIsContextUnlimited = ref(isContextUnlimitedValue);
const tableEnhanceOpenValue = lastHistory.value?.tableEnhanceOpen ?? false;
const localTableEnhanceOpen = ref(tableEnhanceOpenValue);

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

const textInput = ref("");
const linkInputRef = ref<HTMLInputElement | null>(null);
const textInputRef = ref<HTMLElement | null>(null);
const showLinkInput = ref(false);
const newLink = ref("");
const sendDisabled = ref(false);
const tags = ref<TagType.Tag[]>([]);
const tagsLimit = 1;
const isTagsFull = computed(() => tags.value.length >= tagsLimit);
const fileInput = ref<HTMLInputElement | null>(null);

const notification_show = ref(false);
const notification_text = ref("");
const notification_isSuccess = ref(true);

const isLoading = ref(false);

// 控制文件、链接和创建历史的uuid
const uuid = ref<number | null>(null);

const showNotification = (message: string, isSuccess: boolean) => {
  notification_show.value = true;
  notification_text.value = message;
  notification_isSuccess.value = isSuccess;
  setTimeout(() => {
    notification_show.value = false;
  }, 2000);
};

const addLink = async () => {
  if (isLoading.value) {
    return;
  }
  isLoading.value = true;
  if (newLink.value && newLink.value !== "") {
    const expression = /([^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,})/gi;
    const regex = new RegExp(expression);
    if (!newLink.value.match(regex)) {
      showNotification(t("home.linkWrong"), false);
      isLoading.value = false;
      return;
    }
    let res;
    try {
      if (!uuid.value) {
        res = await uploadLink({ link_name: newLink.value });
        if (res.status === "Success") {
          uuid.value = Number(res.message);
        }
      } else {
        res = await uploadLink({ uuid: uuid.value, link_name: newLink.value });
      }
    } catch (e: any) {
      isLoading.value = false;
      let message = t("home.uploadFailed");
      if (e.message === "linkUnavailable") {
        message = t("home.linkUnavailable");
      } else {
        message = t("home.linkFailed");
      }
      showNotification(message, false);
      nextTick(() => {
        linkInputRef.value?.focus();
      });
      return;
    }
    isLoading.value = false;
    tags.value.push({ content: newLink.value, type: "link" });
    newLink.value = "";
    showLinkInput.value = false;
    nextTick(() => {
      (
        textInputRef.value as unknown as { textarea: HTMLTextAreaElement }
      ).textarea?.focus();
    });
  } else {
    isLoading.value = false;
  }
};

const removeTag = (index: number) => {
  // 获取标签的名称，发送请求删除标签
  const content = tags.value[index].content;
  const type = tags.value[index].type;
  if (!uuid || !uuid.value) {
    return;
  } else {
    if (type === "link") {
      const res = removeLink({ uuid: uuid.value, link_name: content });
      tags.value.splice(index, 1);
    } else {
      const res = removePDF({ uuid: uuid.value, file_name: content });
      tags.value.splice(index, 1);
    }
  }
};

const uploadFile = async () => {
  isLoading.value = true;

  const file = fileInput.value?.files?.[0];
  if (!file) {
    isLoading.value = false;
    return;
  }

  if (tags.value.find((tag) => tag.content === file.name)) {
    showNotification(t("home.fileExist"), false);
    isLoading.value = false;
    return;
  }

  let res;
  if (!uuid.value) {
    res = await uploadPDF({ file }).catch((e) => {
      return null;
    });
    if (res && res.message) {
      uuid.value = Number(res.message);
    }
  } else {
    res = await uploadPDF({ uuid: uuid.value, file }).catch(() => null);
  }

  isLoading.value = false;
  if (!res) {
    showNotification(t("home.uploadFailed"), false);
    return;
  }

  tags.value.push({ content: file.name || "error", type: "pdf" });
};

const handleEnter = (event: KeyboardEvent) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
};

const sendMessage = () => {
  if (tags.value.length === 0) {
    showNotification(emptyTagsText.value, false);
    return;
  }
  const my_uuid = uuid?.value ?? 0;
  if (my_uuid === 0) {
    showNotification(emptyTagsText.value, false);
    return;
  }
  if (textInput.value === "") {
    showNotification(emptyContentText.value, false);
    return;
  }
  sendDisabled.value = true;

  let newHistory = {
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
  };

  chatStore.addHistory(newHistory);
  chatStore.addChatByUuid(+my_uuid, {
    chat_id: Date.now(),
    text: textInput.value,
    paragraphs: [],
    dateTime: new Date().toISOString(),
    isUser: true,
    error: false,
    requestOptions: { prompt: "prompt" },
  });
  router.push(`/chat/${my_uuid}`);
  clean();
};

const clean = () => {
  textInput.value = "";
  tags.value = [];
  sendDisabled.value = false;
};

const toggleLinkInput = () => {
  showLinkInput.value = !showLinkInput.value;
  if (showLinkInput.value) {
    nextTick(() => {
      linkInputRef.value?.focus();
    });
  }
};

const triggerFileInput = () => {
  if (!fileInput.value) return;
  fileInput.value.click();
};

const handleFileChange = (event: Event) => {
  if (isLoading.value) {
    return;
  }
  const target = event.target as HTMLInputElement;
  if (!target || !target.files) return;
  const file = target.files[0];
  if (file && file.type === "application/pdf") {
    uploadFile();
  } else {
    showNotification(t("home.fileTypeWrong"), false);
  }
};

// onMounted(() => {
//   nextTick(() => {
//     textInputRef.value?.focus();
//   });
// });
</script>

<style></style>
<!-- <button
              @click="triggerFileInput"
              class="text-gray-500 hover:text-gray-700 tooltip tooltip-bottom"
              :data-tip="toolbarUploadTip"
              :disabled="isLoading"
            >
              <DocumentPlusIcon class="w-6 h-6" />
            </button>
            <input
              type="file"
              ref="fileInput"
              accept="application/pdf"
              style="display: none"
              @change="handleFileChange"
            /> -->
