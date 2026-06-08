<template>
  <div
    class="w-full max-w-3xl py-1"
    @mouseover="showEditAndTime = true"
    @mouseleave="showEditAndTime = false"
  >
    <!-- 用户回复 -->
    <div v-if="props.isUser" class="relative flex justify-end">
      <p
        v-show="showEditAndTime"
        class="absolute mt-1 text-xs text-gray-500 right-1 -top-6"
      >
        {{ new Date(props.dateTime).toLocaleString() }}
      </p>
      <div
        class="relative max-w-2xl px-4 py-2 rounded-lg shadow-md bg-base-200"
      >
        <p class="leading-snug whitespace-pre-line text-md text-base-content">
          {{ renderText }}
        </p>
      </div>
    </div>
    <!-- 模型回答 -->
    <div v-else class="relative flex justify-start max-w-3xl">
      <p
        v-show="showEditAndTime"
        class="absolute mt-1 text-xs text-gray-500 -top-6"
      >
        {{ new Date(props.dateTime).toLocaleString() }}
      </p>
      <div
        class="relative px-4 py-6 shadow-md bg-base-100 rounded-2xl"
        ref="textRef"
      >
        <span
          v-html="renderText"
          :class="{
            'my-markdown-body prose text-base-content inline': true,
            'text-red-500': props.error,
          }"
        />
        <!-- 工具栏 -->
        <div
          class="flex items-center justify-between pt-4 mt-4 border-t border-gray-400"
          data-html2canvas-ignore="true"
        >
          <div class="flex space-x-2">
            <button
              class="btn btn-xs btn-ghost tooltip tooltip-top"
              :data-tip="copyTipText"
              @click="handleCopy"
              aria-label="Copy"
            >
              <Icon
                name="material-symbols:content-copy"
                class="w-5 h-5 text-gray-500"
              />
            </button>
            <button
              v-if="!props.loading"
              class="btn btn-xs btn-ghost tooltip tooltip-top"
              :data-tip="retryTipText"
              @click="handleRetry"
              aria-label="Retry"
            >
              <Icon
                name="material-symbols-light:directory-sync-rounded"
                class="w-5 h-5 text-gray-500"
              />
            </button>
          </div>

          <div class="flex ml-10 space-x-2">
            <transition name="fade">
              <button
                v-if="!props.loading"
                class="btn btn-xs btn-ghost tooltip tooltip-top"
                :data-tip="likeTipText"
                @click="handleLike"
                aria-label="Like"
              >
                <Icon
                  :name="
                    props.isGood === true
                      ? 'icon-park-solid:good-one'
                      : 'icon-park-outline:good-one'
                  "
                  :class="[
                    'w-5 h-5 transition-colors duration-300',
                    props.isGood === true ? 'text-blue-500' : 'text-gray-500',
                  ]"
                />
              </button>
            </transition>
            <transition name="fade">
              <button
                v-if="!props.loading"
                class="btn btn-xs btn-ghost tooltip tooltip-top"
                :data-tip="dislikeTipText"
                @click="handleDislike"
                aria-label="Dislike"
              >
                <Icon
                  :name="
                    props.isGood === false
                      ? 'icon-park-solid:bad-one'
                      : 'icon-park-outline:bad-one'
                  "
                  :class="[
                    'w-5 h-5 transition-colors duration-300',
                    props.isGood === false ? 'text-gray-500' : 'text-gray-500',
                  ]"
                />
              </button>
            </transition>
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
import Notification from "@/components/Notification.vue";
import { copyToClip } from "@/utils/copy";
// @ts-ignore
import { useNuxtApp } from "#app";
const nuxtApp = useNuxtApp();
const mdRenderer = nuxtApp.$mdRenderer as any;
import { useI18n } from "vue-i18n";
const { t } = useI18n();
const copySuccessText = t("chat.copySuccess");
const copyTipText = t("chat.copyTip");
const retryTipText = t("chat.retryTip");
const likeTipText = t("chat.likeTip");
const dislikeTipText = t("chat.dislikeTip");

const showEditAndTime = ref(false);

const notification_show = ref(false);
const notification_text = ref("");
const notification_isSuccess = ref(true);

const textRef = ref<HTMLElement>();

const props = defineProps({
  isUser: { type: Boolean, default: false },
  text: { type: String, default: "" },
  dateTime: { type: String, default: "" },
  error: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  index: { type: Number, default: 0 },
  isGood: {
    type: [Boolean, null] as PropType<true | false | undefined>,
    default: undefined,
  },
});

const renderText = computed(() => {
  try {
    if (props.loading) {
      return mdRenderer.render(props.text, props.index);
    } else {
      const value = props.text ?? "";
      return props.isUser ? value : mdRenderer.render(value, props.index);
    }
  } catch (error) {
    return props.text ?? "";
  }
});

const showNotification = (message: string, isSuccess: boolean) => {
  notification_show.value = true;
  notification_text.value = message;
  notification_isSuccess.value = isSuccess;
  setTimeout(() => {
    notification_show.value = false;
  }, 2000);
};

const emit = defineEmits([
  "handleFootnoteClick",
  "handleRetry",
  "handleLike",
  "handleDislike",
  "handleDelete",
]);

const handleCopy = async () => {
  await copyToClip(props.text);
  showNotification(copySuccessText, true);
};

const handleRetry = () => {
  emit("handleRetry");
};

const handleLike = () => {
  emit("handleLike");
};

const handleDislike = () => {
  emit("handleDislike");
};

const handleDelete = () => {
  emit("handleDelete");
};

const handleFootnoteClick = (ref: Element) => {
  emit("handleFootnoteClick", ref);
};

const addFootnoteClickEvents = () => {
  if (textRef.value) {
    const footnoteRefs = textRef.value.querySelectorAll(".footnote-ref");
    footnoteRefs.forEach((ref) => {
      ref.addEventListener("click", () => {
        handleFootnoteClick(ref);
      });
    });
  }
};

const addCopyEvents = () => {
  if (textRef.value) {
    const copyBtn = textRef.value.querySelectorAll(".code-block-header__copy");
    copyBtn.forEach((btn) => {
      btn.addEventListener("click", () => {
        const code = btn.parentElement?.nextElementSibling?.textContent;
        if (code) {
          copyToClip(code).then(() => {
            showNotification(copySuccessText, true);
          });
        }
      });
    });
  }
};

const removeCopyEvents = () => {
  if (textRef.value) {
    const copyBtn = textRef.value.querySelectorAll(".code-block-header__copy");
    copyBtn.forEach((btn) => {
      btn.removeEventListener("click", () => {});
    });
  }
};

const removeFootnoteClickEvents = () => {
  if (textRef.value) {
    const footnoteRefs = textRef.value.querySelectorAll(".footnote-ref");
    footnoteRefs.forEach((ref) => {
      ref.removeEventListener("click", () => {});
    });
  }
};

onMounted(() => {
  addCopyEvents();
  addFootnoteClickEvents();
});

onUpdated(() => {
  addCopyEvents();
  addFootnoteClickEvents();
});

onUnmounted(() => {
  removeCopyEvents();
  removeFootnoteClickEvents();
});
</script>

<style lang="less">
@import url(./message.less);
</style>
