<template>
  <div class="fixed inset-0 flex flex-col">
    <!-- 固定顶部导航栏 -->
    <div
      :class="`fixed top-0 z-50 flex items-center w-full h-16 border-b ${
        isDrawerOpen ? 'left-[24rem]' : 'left-16'
      } bg-base-100 border-slate-300`"
    >
      <div class="flex items-center justify-between w-full px-4">
        <div
          class="w-1/3 overflow-hidden text-sm font-semibold text-gray-400 truncate whitespace-nowrap"
        >
          {{ history?.title ?? "" }}
        </div>
        <div :class="`${isDrawerOpen ? 'mr-96' : 'mr-16'}`">
          <button
            v-if="isOpen"
            class="h-10 btn-sm btn btn-ghost tooltip tooltip-bottom"
            :data-tip="closeDrawerTip"
            @click="buttonToggleDrawer"
          >
            <Icon name="lucide:panel-right-close" class="w-7 h-7" />
          </button>
          <button
            v-else
            class="h-10 btn-sm btn btn-ghost tooltip tooltip-bottom"
            :data-tip="openDrawerTip"
            @click="buttonToggleDrawer"
          >
            <Icon name="lucide:panel-right-open" class="w-7 h-7" />
          </button>
          <button
            class="h-10 btn-sm btn btn-ghost tooltip tooltip-bottom"
            :data-tip="shareTip"
            @click="handleExport"
          >
            <Icon name="lucide:share-2" class="w-7 h-7" />
          </button>
        </div>
      </div>
    </div>

    <!-- 主内容 -->
    <main
      class="flex flex-col flex-1 pt-16 pb-6 overflow-hidden bg-base-300"
      :class="paraDrawerClass"
      :style="paraDrawerStyle"
    >
      <div
        class="flex-1 overflow-y-auto no-scrollbar"
        ref="conversationListRef"
        @scroll="handleScroll"
      >
        <div class="max-w-screen-xl m-auto bg-base-300" id="image-wrapper">
          <!-- 论文标题 -->
          <h1 class="p-6 text-2xl font-bold text-center text-base-content">
            {{ history?.paperTitle ?? "" }}
          </h1>
          <!-- 对话列表 -->
          <div class="flex flex-col items-center p-4 space-y-6 overflow-auto">
            <template v-for="(item, index) in dataSources" :key="index">
              <Message
                :isUser="item.isUser"
                :text="item.text"
                :dateTime="item.dateTime"
                :error="item.error"
                :loading="item.loading"
                :index="index"
                :isGood="item.isGood"
                @handleFootnoteClick="handleFootnoteClick"
                @handleRetry="handleRetry(index)"
                @handleLike="handleLike(index)"
                @handleDislike="handleDislike(index)"
                @handleDelete="handleDelete(index)"
              />
              <div
                v-if="!history?.isContextUnlimited && index === computedIndex"
                class="flex items-center justify-center divider text-base-content"
                data-html2canvas-ignore="true"
              >
                <Icon name="mdi:arrow-down-thin" class="w-10 h-10 -mr-4" />
                {{ contextDivider }}
              </div>
            </template>
          </div>
          <div
            class="flex-col items-center hidden w-full p-4 space-y-2 border-t border-gray-400"
            id="footer-info"
          >
            <img
              :src="isdark ? '/favicon-dark.ico' : '/favicon-light.ico'"
              alt="Logo"
              class="size-8"
            />
            <p class="text-sm text-base-content">{{ currentHref }}</p>
          </div>
        </div>
      </div>
    </main>

    <!-- 包含输入框和按钮的容器 -->
    <div
      class="relative w-full bg-base-300"
      :class="paraDrawerClass"
      :style="paraDrawerStyle"
    >
      <div class="relative w-full max-w-3xl pb-20 mx-auto">
        <ChatTextInput
          ref="inputRef"
          v-model="prompt"
          :loading="loading"
          :temperature="history?.temperature ?? 0.5"
          :contextCount="history?.contextNum ?? 1"
          :paragraphCount="history?.paragraphNum ?? 5"
          :isContextUnlimited="history?.isContextUnlimited ?? true"
          :tableEnhanceOpen="history?.tableEnhanceOpen ?? false"
          @handleSubmit="handleSubmit"
          @handleStop="handleStop"
          @keypress="handleEnter"
          @update:temperature="updateTemperature"
          @update:contextCount="updateContextCount"
          @update:paragraphCount="updateParagraphCount"
          @update:isContextUnlimited="updateIsContextUnlimited"
          @update:tableEnhanceOpen="updateTableEnhanceOpen"
        />

        <!-- 向下箭头按钮，绝对定位在输入框的右侧上方 -->
        <button
          v-if="showScrollDownArrow"
          @click="scrollToBottom"
          class="absolute top-[-0.4rem] right-0 p-2 mr-2 transform -translate-y-full rounded-full shadow-lg bg-base-200"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="w-6 h-6 text-gray-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </button>
      </div>
    </div>

    <ParagraphDrawer
      :isOpen="isOpen"
      :isLoading="isLoading"
      :paragraphs="paragraphs"
      :highlightNumber="highlightNumber"
      @closeDrawer="toggleDrawer"
    />

    <ScreenshotModal
      :isVisible="isModalVisible"
      :screenshotDataUrl="screenshotDataUrl"
      @close="
        isModalVisible = false;
        screenshotDataUrl = '';
      "
    />

    <Drawer />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick, onUnmounted } from "vue";
import { fetchParagraphAPI, fetchChatAPIProcess, fetchLikeAPI } from "@/api";
import { useRoute } from "vue-router";
import { useDrawerStore } from "@/store";
import Drawer from "@/components/Drawer.vue";
import {
  Message,
  ScreenshotModal,
  ChatTextInput,
  ParagraphDrawer,
} from "./components";

import { useChat } from "@/pages/chat/hooks/useChat";
import { useChatStore } from "@/store";
import { useParaDrawerStore } from "@/store";
import html2canvas from "html2canvas-pro";
import { useI18n } from "vue-i18n";
const { t } = useI18n();
const shareTip = computed(() => t("chat.screenshotModal.title"));
const openDrawerTip = computed(() => t("chat.openDrawerTip"));
const closeDrawerTip = computed(() => t("chat.closeDrawerTip"));
const contextDivider = computed(() => t("chat.contextDivider"));

const { addChat, updateChat, updateChatSome, getChatByUuidAndIndex } =
  useChat();

const paraDrawerStore = useParaDrawerStore();
const chatStore = useChatStore();
const router = useRouter();
chatStore.initRouter(router);

const drawerStore = useDrawerStore();
const isDrawerOpen = computed(() => drawerStore.isDrawerOpen);

const paraDrawerClass = computed(() => ({
  "pl-[24rem]": isDrawerOpen.value,
  "pl-[4rem]": !isDrawerOpen.value,
}));

const paraDrawerRem = computed(() => paraDrawerStore.drawerWidth);
const paraDrawerStyle = computed(() => ({
  paddingRight: isOpen.value ? `${paraDrawerRem.value}px` : "",
}));

const isModalVisible = ref(false);
const screenshotDataUrl = ref("");

const route = useRoute();
const { uuid } = route.params as { uuid: string };

if (!uuid || !chatStore.getHistoryByUuid(+uuid)) {
  router.push("/");
}
const dataSources = computed(() => chatStore.getChatByUuid(+uuid));
const history = computed(() => chatStore.getHistoryByUuid(+uuid));

const prompt = ref<string>("");
const loading = ref<boolean>(false);
const inputRef = ref<Ref | null>(null);
let controller = new AbortController();

const computedIndex = computed(() => {
  const contextNum = (history.value?.contextNum ?? 1) + 1;
  let count = 0;
  for (let i = dataSources.value.length - 1; i >= 0; i--) {
    if (!dataSources.value[i].isUser) {
      count++;
      if (count === contextNum) {
        return i;
      }
    }
  }
  return -1; // 如果没有找到，返回一个无效的索引
});

// 未知原因刷新页面，loading 状态不会重置，手动重置
dataSources.value.forEach((item, index) => {
  if (item.loading) updateChatSome(+uuid, index, { loading: false });
});

if ((history.value?.isFirst ?? false) && dataSources.value.length > 1) {
  chatStore.updateHistory(+uuid, { isFirst: false });
}

const paragraphs = ref<string[]>([]);

const showScrollDownArrow = ref(false);
const conversationListRef = ref<HTMLElement | null>(null);

const handleScroll = () => {
  if (conversationListRef.value) {
    const scrollTop = conversationListRef.value.scrollTop;
    const scrollHeight = conversationListRef.value.scrollHeight;
    const clientHeight = conversationListRef.value.clientHeight;
    const bottomReached =
      Math.abs(scrollHeight - scrollTop - clientHeight) <= 2; // 允许 1 像素的误差

    showScrollDownArrow.value = !bottomReached;
  }
};

const checkInitialScrollPosition = () => {
  if (conversationListRef.value) {
    const scrollTop = conversationListRef.value.scrollTop;
    const scrollHeight = conversationListRef.value.scrollHeight;
    const clientHeight = conversationListRef.value.clientHeight;
    const bottomReached =
      Math.abs(scrollHeight - scrollTop - clientHeight) <= 2; // 允许 1 像素的误差

    showScrollDownArrow.value = !bottomReached;
  }
};

const scrollToBottom = () => {
  nextTick(() => {
    if (conversationListRef.value) {
      conversationListRef.value.scrollTo({
        top: conversationListRef.value.scrollHeight,
        behavior: "smooth",
      });
    }
  });
};

const scrollToBottomIfAtBottom = () => {
  if (conversationListRef.value) {
    const threshold = 100; // 阈值，表示距离底部的距离阈值
    const distanceToBottom =
      conversationListRef.value.scrollHeight -
      conversationListRef.value.scrollTop -
      conversationListRef.value.clientHeight;

    nextTick(() => {
      if (distanceToBottom <= threshold) {
        if (conversationListRef.value) {
          conversationListRef.value.scrollTo({
            top: conversationListRef.value.scrollHeight,
            behavior: "smooth",
          });
        }
      }
    });
  }
};

const getContextQA = (dataSources: Chat.Chat[], index?: number) => {
  if (!history.value) return { past_questions: [], past_answers: [] };

  const { contextNum, isContextUnlimited } = history.value;

  const relevantDataSources =
    index !== undefined ? dataSources.slice(0, index) : dataSources;

  const contextChats = relevantDataSources.filter((item) => !item.isUser);

  if (isContextUnlimited) {
    const pastContextChats =
      index !== undefined ? contextChats : contextChats.slice(0, -1);
    return {
      past_questions: pastContextChats.map(
        (item) => item.requestOptions.prompt
      ),
      past_answers: pastContextChats.map((item) => item.text),
    };
  }

  const startIndex =
    index === undefined
      ? Math.max(0, contextChats.length - contextNum - 1)
      : Math.max(0, contextChats.length - contextNum - 1);
  const selectedChats = contextChats.slice(startIndex, contextChats.length - 1);
  return {
    past_questions: selectedChats.map((item) => item.requestOptions.prompt),
    past_answers: selectedChats.map((item) => item.text),
  };
};

const handleEnter = (event: KeyboardEvent) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    handleSubmit();
  }
};

const handleStop = () => {
  if (loading.value) {
    controller.abort();
    loading.value = false;
  }
};

const handleDelete = (index: number) => {
  if (loading.value) return;
  chatStore.deleteChatByUuid(+uuid, index);
};

const handleExport = async () => {
  if (loading.value) return;
  isModalVisible.value = true;
  await updateIsDark();
  const ele = document.getElementById("image-wrapper");
  const footerInfo = document.getElementById("footer-info");
  if (!ele || !footerInfo) return;
  // 显示 footer-info
  footerInfo.classList.remove("hidden");
  footerInfo.classList.add("flex");

  const canvas = await html2canvas(ele as HTMLDivElement, {
    useCORS: true,
    allowTaint: false,
    scale: 4,
  });

  // 截图完成后隐藏 footer-info
  footerInfo.classList.remove("flex");
  footerInfo.classList.add("hidden");

  screenshotDataUrl.value = canvas.toDataURL("screenshot/png");
};

const handleSubmit = () => {
  onConversation();
};

const addThinkingMessage = (uuid: number, message: string, chat_id: number) => {
  addChat(uuid, {
    chat_id: chat_id,
    text: t("chat.thinking"),
    paragraphs: [],
    dateTime: new Date().toISOString(),
    isUser: false,
    error: false,
    loading: true,
    requestOptions: { prompt: message },
  });
  scrollToBottom();
};

const loadParagraphs = async (
  uuid: number,
  chat_id: number,
  question: string,
  controller: AbortController
): Promise<boolean> => {
  isLoading.value = true;
  try {
    const response = await fetchParagraphAPI({
      uuid: uuid,
      chat_id: chat_id,
      paragraph_number: history.value?.paragraphNum ?? 5,
      question: question,
      signal: controller.signal,
    });
    updateChatSome(uuid, dataSources.value.length - 1, {
      paragraphs: response.data.paragraphs,
      dateTime: new Date().toISOString(),
    });
    chatStore.updateHistory(+uuid, {
      paperTitle: response.data.paperTitle,
      updatedAt: new Date().toISOString(),
    });
    paragraphs.value = response.data.paragraphs;
    oldChatIndex.value = dataSources.value.length - 1;
    highlightNumber.value = 0;
    isLoading.value = false;
    return true;
  } catch (error: any) {
    isLoading.value = false;
    paragraphs.value = [];
    oldChatIndex.value = dataSources.value.length - 1;
    highlightNumber.value = 0;
    if (error.message === "canceled") {
      updateChatSome(uuid, dataSources.value.length - 1, { loading: false });
      scrollToBottomIfAtBottom();
    }
    return false;
  }
};

const fetchChatAPI = async (
  uuid: number,
  chat_id: number,
  message: string,
  past_questions: string[],
  past_answers: string[],
  controller: AbortController
) => {
  let accumulatedResponseText = "";
  try {
    await fetchChatAPIProcess({
      question: message,
      options: {
        uuid: uuid,
        chat_id: chat_id,
        temperature: history.value?.temperature ?? 0.6,
        past_questions: past_questions,
        past_answers: past_answers,
        paragraph_number: history.value?.paragraphNum ?? 5,
        need_table: history.value?.tableEnhanceOpen ?? false,
      },
      signal: controller.signal,
      onDownloadProgress: ({ event }) => {
        const xhr = event.target;
        const { responseText } = xhr;

        try {
          accumulatedResponseText += responseText.slice(
            accumulatedResponseText.length
          );
          updateChatSome(uuid, dataSources.value.length - 1, {
            text: accumulatedResponseText,
            dateTime: new Date().toISOString(),
          });
          scrollToBottomIfAtBottom();
        } catch (error) {}
      },
    });
    updateChatSome(uuid, dataSources.value.length - 1, { loading: false });
  } catch (error: any) {
    handleFetchError(uuid, error, message);
  }
};

const handleFetchError = (uuid: number, error: any, message: string) => {
  let errorMessage = error?.message ?? t("common.wrong");
  // console.log("errorMessage", errorMessage);

  if (error.message === "canceled") {
    updateChatSome(uuid, dataSources.value.length - 1, { loading: false });
    scrollToBottomIfAtBottom();
    return;
  }
  errorMessage = t("common.wrong");
  const currentChat = getChatByUuidAndIndex(uuid, dataSources.value.length - 1);
  if (currentChat?.text && currentChat.text !== "") {
    updateChatSome(uuid, dataSources.value.length - 1, {
      text: `${currentChat.text}\n[${errorMessage}]`,
      error: true,
      loading: false,
    });
    return;
  }
  updateChatSome(uuid, dataSources.value.length - 1, {
    text: errorMessage,
    error: true,
    loading: false,
  });
  scrollToBottomIfAtBottom();
};

const firstConversation = async () => {
  loading.value = true;
  const message = dataSources.value[0].text;
  const chat_id = dataSources.value[0].chat_id;
  addThinkingMessage(+uuid, message, chat_id);

  controller = new AbortController();
  const loadParagraphsSuccess = await loadParagraphs(
    +uuid,
    chat_id,
    message,
    controller
  );

  if (loadParagraphsSuccess) {
    controller = new AbortController();
    const { past_questions, past_answers } = getContextQA(dataSources.value);
    await fetchChatAPI(
      +uuid,
      chat_id,
      message,
      past_questions,
      past_answers,
      controller
    );
  }
  loading.value = false;
  isLoading.value = false;
  chatStore.updateHistory(+uuid, {
    isFirst: false,
    updatedAt: new Date().toISOString(),
  });
};

const onConversation = async () => {
  const message = prompt.value;
  if (loading.value || !message || message.trim() === "") return;
  const chat_id = Date.now();

  // 首先添加用户输入的对话
  addChat(+uuid, {
    chat_id: chat_id,
    text: message,
    paragraphs: [],
    dateTime: new Date().toISOString(),
    isUser: true,
    error: false,
    requestOptions: { prompt: message },
  });
  scrollToBottom();

  loading.value = true;
  prompt.value = "";

  addThinkingMessage(+uuid, message, chat_id);

  controller = new AbortController();
  const loadParagraphsSuccess = await loadParagraphs(
    +uuid,
    chat_id,
    message,
    controller
  );

  if (loadParagraphsSuccess) {
    controller = new AbortController();
    const { past_questions, past_answers } = getContextQA(dataSources.value);
    await fetchChatAPI(
      +uuid,
      chat_id,
      message,
      past_questions,
      past_answers,
      controller
    );
  }

  loading.value = false;
  isLoading.value = false;
};

const handleFootnoteClick = (ref: Element) => {
  const dataId = ref.getAttribute("data-id");

  if (dataId !== null) {
    const [chatIndex, footnoteId] = dataId.split("-");

    if (
      oldChatIndex.value !== parseInt(chatIndex) &&
      oldChatIndex.value !== -1
    ) {
      if (!isOpen.value) {
        paraDrawerStore.setDrawerWidth(paraDrawerStore.lastValidWidth);
        isOpen.value = true;
        oldChatIndex.value = parseInt(chatIndex);
        paragraphs.value = dataSources.value[parseInt(chatIndex)].paragraphs;
        highlightNumber.value = parseInt(footnoteId);
      } else {
        isLoading.value = true;

        setTimeout(() => {
          oldChatIndex.value = parseInt(chatIndex);
          paragraphs.value = dataSources.value[parseInt(chatIndex)].paragraphs;
          highlightNumber.value = parseInt(footnoteId);
          isLoading.value = false;
        }, 300);
      }
    } else {
      paraDrawerStore.setDrawerWidth(paraDrawerStore.lastValidWidth);
      isOpen.value = true;
      oldChatIndex.value = parseInt(chatIndex);
      paragraphs.value = dataSources.value[parseInt(chatIndex)].paragraphs;
      highlightNumber.value = parseInt(footnoteId);
    }
  }
};

const oldChatIndex = ref(-1);
const isOpen = ref(false);
const isLoading = ref(false);
const toggleDrawer = () => {
  isOpen.value = !isOpen.value;
};
const highlightNumber = ref(1);
const buttonToggleDrawer = () => {
  if (paragraphs.value.length === 0) {
    for (let i = dataSources.value.length - 1; i >= 0; i--) {
      if (!dataSources.value[i].isUser) {
        paragraphs.value = dataSources.value[i].paragraphs;
        break;
      }
    }
  }
  paraDrawerStore.setDrawerWidth(paraDrawerStore.lastValidWidth);
  isOpen.value = !isOpen.value;
  scrollToBottomIfAtBottom();
};

const handleRetry = async (index: number) => {
  if (loading.value) return;
  const { requestOptions } = dataSources.value[index];
  let message = requestOptions?.prompt ?? "";
  const chat_id = Date.now();
  loading.value = true;
  addThinkingMessage(+uuid, message, chat_id);
  controller = new AbortController();
  const loadParagraphsSuccess = await loadParagraphs(
    +uuid,
    chat_id,
    message,
    controller
  );
  if (loadParagraphsSuccess) {
    controller = new AbortController();
    const { past_questions, past_answers } = getContextQA(
      dataSources.value,
      index
    );
    await fetchChatAPI(
      +uuid,
      chat_id,
      message,
      past_questions,
      past_answers,
      controller
    );
  }

  loading.value = false;
};

const handleLike = (index: number) => {
  const isGood = dataSources.value[index].isGood;
  if (isGood === undefined || isGood === false) {
    updateChatSome(+uuid, index, { isGood: true });
    fetchLikeAPI({
      uuid: +uuid,
      chat_id: dataSources.value[index].chat_id,
      is_good: true,
    });
  } else {
    updateChatSome(+uuid, index, { isGood: undefined });
  }
};

const handleDislike = (index: number) => {
  const isGood = dataSources.value[index].isGood;
  if (isGood === undefined || isGood === true) {
    updateChatSome(+uuid, index, { isGood: false });
    fetchLikeAPI({
      uuid: +uuid,
      chat_id: dataSources.value[index].chat_id,
      is_good: false,
    });
  } else {
    updateChatSome(+uuid, index, { isGood: undefined });
  }
};

const updateTemperature = (value: number) => {
  chatStore.updateHistory(+uuid, { temperature: value });
};

const updateContextCount = (value: number) => {
  chatStore.updateHistory(+uuid, { contextNum: value });
};

const updateParagraphCount = (value: number) => {
  chatStore.updateHistory(+uuid, { paragraphNum: value });
};

const updateIsContextUnlimited = (value: boolean) => {
  chatStore.updateHistory(+uuid, { isContextUnlimited: value });
};

const updateTableEnhanceOpen = (value: boolean) => {
  chatStore.updateHistory(+uuid, { tableEnhanceOpen: value });
};

onBeforeUnmount(() => {
  if (conversationListRef.value) {
    conversationListRef.value.removeEventListener("scroll", handleScroll);
  }
});

const currentHref = window.location.href.split("/chat")[0];

const isdark = ref(false);
const updateIsDark = async () => {
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme) {
    isdark.value = savedTheme === "dark";
  }
};
onMounted(async () => {
  await nextTick(() => {
    updateIsDark();
    try {
      if (conversationListRef.value) {
        checkInitialScrollPosition();
        conversationListRef.value.addEventListener("scroll", handleScroll);
      }
      scrollToBottom();
    } catch (error) {
      console.error(error);
    }
  });
  if (history.value?.isFirst ?? false) {
    firstConversation();
  }
});

onUnmounted(() => {
  if (loading.value) controller.abort();
});
</script>
