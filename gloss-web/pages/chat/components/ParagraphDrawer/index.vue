<template>
  <div :class="drawerClasses" :style="drawStyle">
    <div
      class="h-full py-5 pl-5 pr-3 overflow-auto bg-base-200 no-scrollbar"
      ref="drawerContent"
    >
      <h2 class="mb-6 text-xl font-bold text-base-content">{{ title }}</h2>
      <div v-if="isLoading" class="flex items-center justify-center h-full">
        <span class="loading loading-infinity loading-lg text-primary"></span>
      </div>
      <ul v-else class="space-y-6" ref="textRef">
        <li
          v-for="(paragraph, index) in processedParagraphs"
          :key="index"
          :ref="setParagraphRef(index)"
          class="relative rounded-lg shadow-lg hover:shadow-xl para-markdown-body"
        >
          <div class="w-full indicator">
            <span
              class="font-semibold indicator-item indicator-start badge badge-lg"
              :class="{
                'badge-neutral': !isHighlighted(index),
                'badge-primary': isHighlighted(index),
              }"
            >
              {{ paragraph.number }}
            </span>
            <div
              class="w-full p-5 rounded-lg"
              :class="{
                'bg-base-100': !isHighlighted(index),
                'bg-base-100 ring-2 ring-primary': isHighlighted(index),
              }"
            >
              <p
                class="overflow-x-auto overflow-y-hidden break-words my-markdown-body"
              >
                <span
                  v-html="mdRenderer.render(paragraph.content)"
                  class="prose prose-lg prose-img:rounded-xl prose-headings:text-base-content prose-a:text-primary"
                ></span>
              </p>
            </div>
          </div>
        </li>
      </ul>
    </div>
    <div
      class="absolute top-0 left-0 h-full border opacity-50 border-slate-400 cursor-ew-resize"
      @mousedown="startResizing"
    ></div>
  </div>
  <Notification
    :show="notification_show"
    :text="notification_text"
    :isSuccess="notification_isSuccess"
  />
</template>

<script setup>
import { computed, nextTick, onUpdated, watch, ref } from "vue";
import { defineProps, defineEmits } from "vue";
import Notification from "@/components/Notification.vue";
import { copyToClip } from "@/utils/copy";
import { useParaDrawerStore } from "@/store";
const paraDrawerStore = useParaDrawerStore();
// @ts-ignore
import { useNuxtApp } from "#app";
const nuxtApp = useNuxtApp();
const mdRenderer = nuxtApp.$mdRenderer;

import { useI18n } from "vue-i18n";
const { t } = useI18n();
const title = t("paragraph.title");
const copySuccessText = t("chat.copySuccess");

const props = defineProps({
  isOpen: Boolean,
  isLoading: Boolean,
  paragraphs: Array,
  highlightNumber: Number,
});

const notification_show = ref(false);
const notification_text = ref("");
const notification_isSuccess = ref(true);
const textRef = ref();
const isCopying = ref(false);
let scrollTimer = null;

const emits = defineEmits(["closeDrawer"]);

const paragraphRefs = ref([]);
const drawerContent = ref(null);

const drawerClasses = computed(
  () =>
    `fixed top-16 right-0 h-[calc(100%-4rem)] bg-base-200 z-0 transition-transform transform ${
      props.isOpen ? "translate-x-0" : "translate-x-full"
    }`
);
const paraDrawerRem = computed(() => paraDrawerStore.drawerWidth);
const drawStyle = computed(() => ({
  width: `${paraDrawerRem.value}px`,
}));

let isResizing = false;
const closeThreshold = 70;
const maxSidebarWidth = window.innerWidth - 64;
const startResizing = (event) => {
  isResizing = true;
  document.addEventListener("mousemove", resize);
  document.addEventListener("mouseup", stopResizing);
  document.body.style.userSelect = "none";
};

const resize = (event) => {
  if (isResizing) {
    const newWidth = window.innerWidth - event.clientX;
    if (newWidth <= maxSidebarWidth) {
      paraDrawerStore.setDrawerWidth(newWidth);
    }
    if (newWidth < closeThreshold) {
      emits("closeDrawer");
    }
  }
};

const stopResizing = (event) => {
  isResizing = false;
  document.removeEventListener("mousemove", resize);
  document.removeEventListener("mouseup", stopResizing);
  document.body.style.userSelect = "";
  const newWidth = window.innerWidth - event.clientX;
  if (paraDrawerStore.drawerWidth >= closeThreshold) {
    paraDrawerStore.setLastValidWidth(paraDrawerStore.drawerWidth);
  }
  if (newWidth < closeThreshold) {
    emits("closeDrawer");
  }
};

// 判断当前段落是否包含被点击的 [n] 标记
const isHighlighted = (index) => {
  const p = props.paragraphs?.[index];
  if (!p) return false;
  return new RegExp(`\\[${props.highlightNumber}\\]`).test(p);
};

// 在抽屉打开时滚动到高亮的段落
const scrollToHighlighted = () => {
  nextTick(() => {
    const highlightedIndex = props.paragraphs.findIndex((paragraph) =>
      new RegExp(`\\[${props.highlightNumber}\\]`).test(paragraph ?? "")
    );
    if (highlightedIndex !== -1 && paragraphRefs.value[highlightedIndex]) {
      const offsetTop =
        drawerContent.value.scrollTop +
        paragraphRefs.value[highlightedIndex].getBoundingClientRect().top -
        80;

      drawerContent.value.scrollTo({
        top: offsetTop,
        behavior: "smooth",
      });
    }
  });
};

watch(
  () => props.highlightNumber,
  (newHighlightNumber, oldHighlightNumber) => {
    if (newHighlightNumber !== oldHighlightNumber) {
      scrollToHighlighted();
    }
  }
);

watch(
  () => props.isOpen,
  (newIsOpen) => {
    if (newIsOpen) {
      scrollToHighlighted();
    }
  }
);

watch(
  () => props.isLoading,
  (newIsLoading) => {
    if (newIsLoading) {
      isCopying.value = false;
      scrollTimer = null;
    }
  }
);

onUpdated(() => {
  if (!isCopying.value && props.isOpen) {
    scrollToHighlighted();
  }
  addCopyEvents();
});

const processedParagraphs = computed(() => {
  if (!props.paragraphs) return [];
  return props.paragraphs.map((paragraph) => {
    if (typeof paragraph !== "string") return { number: "", content: "" };
    const numbers = [...paragraph.matchAll(/\[(\d+)\]/g)].map((m) => m[1]);
    const content = paragraph.replace(/\s*\[\d+\]/g, "").trim();
    return {
      number: numbers.join(" "),
      content,
    };
  });
});

const setParagraphRef = (index) => (el) => {
  nextTick(() => {
    if (!paragraphRefs.value) paragraphRefs.value = [];
    paragraphRefs.value[index] = el;
  });
};

const addCopyEvents = () => {
  if (textRef.value) {
    const copyBtn = textRef.value.querySelectorAll(".code-block-header__copy");
    copyBtn.forEach((btn) => {
      btn.addEventListener("click", () => {
        const code = btn.parentElement?.nextElementSibling?.textContent;
        if (code) {
          isCopying.value = true;
          if (scrollTimer !== null) {
            clearTimeout(scrollTimer);
          }
          copyToClip(code).then(() => {
            notification_show.value = true;
            notification_text.value = copySuccessText;
            notification_isSuccess.value = true;
            setTimeout(() => {
              notification_show.value = false;
            }, 2000);
            scrollTimer = setTimeout(() => {
              isCopying.value = true;
              scrollTimer = null;
            }, 100);
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

onMounted(() => {
  addCopyEvents();
});

onUnmounted(() => {
  removeCopyEvents();
  if (scrollTimer !== null) {
    clearTimeout(scrollTimer);
  }
});
</script>

<style lang="less">
@import url(./paragraph.less);
</style>
