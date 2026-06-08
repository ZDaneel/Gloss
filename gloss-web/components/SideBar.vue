<template>
  <div class="flex flex-row h-full">
    <div
      class="fixed top-0 left-0 z-50 flex flex-col items-center w-16 h-full border-r bg-base-100 border-slate-300"
    >
      <div class="mt-4">
        <img
          :src="isdark ? '/favicon-dark.ico' : '/favicon-light.ico'"
          alt="Logo"
          class="size-8"
          @click="jumpToHome"
        />
      </div>
      <div class="flex flex-col items-center justify-center flex-grow">
        <button
          class="mb-4 tooltip tooltip-right"
          :data-tip="addTip"
          @click="jumpToHome"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="size-8"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M2.25 12.76c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 0 1 1.037-.443 48.282 48.282 0 0 0 5.68-.494c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z"
            />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M12 7.25v5.5M9.25 10h5.5"
            />
          </svg>
        </button>
        <button
          :class="[
            'mt-4 tooltip tooltip-right flex items-center justify-center p-2 rounded',
            { 'bg-base-300 w-full': isDrawerOpen },
          ]"
          :data-tip="chatTip"
          @click="toggleDrawer"
        >
          <ChatBubbleLeftEllipsisIcon class="size-8" />
        </button>
      </div>
      <!-- 日月 -->
      <div>
        <label class="swap swap-rotate">
          <input
            type="checkbox"
            class="theme-controller"
            :checked="isdark"
            @change="toggleDarkMode"
          />
          <svg
            :class="{
              'rotate-180': isdark,
              'transition-transform duration-300': true,
            }"
            class="fill-current size-8 swap-off"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
          >
            <path
              d="M5.64,17l-.71.71a1,1,0,0,0,0,1.41,1,1,0,0,0,1.41,0l.71-.71A1,1,0,0,0,5.64,17ZM5,12a1,1,0,0,0-1-1H3a1,1,0,0,0,0,2H4A1,1,0,0,0,5,12Zm7-7a1,1,0,0,0,1-1V3a1,1,0,0,0-2,0V4A1,1,0,0,0,12,5ZM5.64,7.05a1,1,0,0,0,.7.29,1,1,0,0,0,.71-.29,1,1,0,0,0,0-1.41l-.71-.71A1,1,0,0,0,4.93,6.34Zm12,.29a1,1,0,0,0,.7-.29l.71-.71a1,1,0,1,0-1.41-1.41L17,5.64a1,1,0,0,0,0,1.41A1,1,0,0,0,17.66,7.34ZM21,11H20a1,1,0,0,0,0,2h1a1,1,0,0,0,0-2Zm-9,8a1,1,0,0,0-1,1v1a1,1,0,0,0,2,0V20A1,1,0,0,0,12,19ZM18.36,17A1,1,0,0,0,17,18.36l.71.71a1,1,0,0,0,1.41,0,1,1,0,0,0,0-1.41ZM12,6.5A5.5,5.5,0,1,0,17.5,12,5.51,5.51,0,0,0,12,6.5Zm0,9A3.5,3.5,0,1,1,15.5,12,3.5,3.5,0,0,1,12,15.5Z"
            />
          </svg>
          <svg
            :class="{
              'rotate-180': !isdark,
              'transition-transform duration-300': true,
            }"
            class="fill-current size-8 swap-on"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
          >
            <path
              d="M21.64,13a1,1,0,0,0-1.05-.14,8.05,8.05,0,0,1-3.37.73A8.15,8.15,0,0,1,9.08,5.49a8.59,8.59,0,0,1,.25-2A1,1,0,0,0,8,2.36,10.14,10.14,0,1,0,22,14.05,1,1,0,0,0,21.64,13Zm-9.5,6.69A8.14,8.14,0,0,1,7.08,5.22v.27A10.15,10.15,0,0,0,17.22,15.63a9.79,9.79,0,0,0,2.1-.22A8.11,8.11,0,0,1,12.14,19.73Z"
            />
          </svg>
        </label>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { ChatBubbleLeftEllipsisIcon } from "@heroicons/vue/24/outline";
import { useDrawerStore } from "@/store";
const router = useRouter();
const drawerStore = useDrawerStore();
const isDrawerOpen = computed(() => drawerStore.isDrawerOpen);
const toggleDrawer = () => {
  drawerStore.toggleDrawer();
};

import { useI18n } from "vue-i18n";
const { t } = useI18n();
const addTip = computed(() => t("sideBar.addTip"));
const chatTip = computed(() => t("sideBar.chatTip"));

const isdark = ref(false);
const toggleDarkMode = () => {
  isdark.value = !isdark.value;
};

const applyTheme = (isDark) => {
  document.documentElement.setAttribute(
    "data-theme",
    isDark ? "dark" : "light"
  );
  localStorage.setItem("theme", isDark ? "dark" : "light");
};

const jumpToHome = () => {
  // 首先判断isDrawerOpen是否为true，如果为true则关闭侧边栏
  if (isDrawerOpen.value) {
    toggleDrawer();
  }

  // 使用 Nuxt3 的路由跳转
  router.push("/");
};

onMounted(() => {
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme) {
    isdark.value = savedTheme === "dark";
  }
  applyTheme(isdark.value);
});

watch(isdark, (newVal) => {
  applyTheme(newVal);
});
</script>

<style>
.swap-rotate .rotate-180 {
  transform: rotate(90deg);
}
</style>
~/store/modules/drawer/drawer
