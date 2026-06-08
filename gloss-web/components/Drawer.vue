<template>
  <div :class="drawerClasses" style="width: 20rem">
    <button
      @click="toggleDrawer"
      class="absolute text-gray-500 top-4 right-4 hover:text-gray-800"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="w-6 h-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M6 18L18 6M6 6l12 12"
        />
      </svg>
    </button>
    <div class="h-full p-4 overflow-y-auto no-scrollbar">
      <h2 class="mb-4 text-2xl font-semibold">
        {{ drawerTitle }}
      </h2>
      <ul class="space-y-4">
        <li
          v-for="history in histories"
          :key="history.uuid"
          class="flex items-center justify-between p-4 text-sm rounded-lg shadow-md cursor-pointer bg-base-100 hover:bg-base-300"
          @click="openTopic(history.uuid)"
        >
          <div class="flex-1 min-w-0">
            <div class="relative overflow-hidden">
              <input
                v-if="history.isEdit"
                v-model="history.title"
                @keypress.enter="saveEdit(history, false, $event)"
                @focusout="saveEdit(history, false, $event)"
                class="w-full p-2 border border-blue-400 rounded bg-base-100 focus:outline-none"
                :ref="(el) => setRef(el as HTMLInputElement, history)"
                @click.stop
              />
              <span v-else class="block pr-6 text-lg font-semibold truncate">
                {{ history.title }}
              </span>
              <p class="mt-1 text-xs text-gray-400">
                {{ new Date(history.updatedAt).toLocaleString() }}
              </p>
            </div>
          </div>
          <div class="flex items-center space-x-3">
            <button
              v-if="!history.isEdit"
              @click="editTitle(history, true, $event)"
              class="text-blue-500 transition-colors duration-300 hover:text-blue-700 tooltip tooltip-top"
              :data-tip="editTip"
            >
              <PencilSquareIcon class="w-5 h-5" />
            </button>
            <button
              v-if="!history.isEdit"
              @click="openDeleteModal(history, $event)"
              class="text-red-500 transition-colors duration-300 hover:text-red-700 tooltip tooltip-top"
              :data-tip="deleteTip"
            >
              <TrashIcon class="w-5 h-5" />
            </button>
          </div>
        </li>
      </ul>
    </div>
  </div>
  <!-- 删除弹窗 -->
  <DeleteModal
    :isVisible="isDeleteModalVisible"
    :title="selectedHistory.title"
    :uuid="selectedHistory.uuid"
    @close="isDeleteModalVisible = false"
    @confirmDelete="handleConfirmDeleteDebounce"
  />
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from "vue";
import { useDrawerStore } from "@/store";
import { useRouter } from "vue-router";
import { useChatStore } from "@/store";
import { useChat } from "@/pages/chat/hooks/useChat";
import {
  PencilSquareIcon,
  TrashIcon,
  CheckCircleIcon,
} from "@heroicons/vue/24/outline";
import DeleteModal from "@/components/DeleteModal.vue";
import { debounce } from "@/utils/functions/debounce";
import { useI18n } from "vue-i18n";
const { t } = useI18n();
const drawerTitle = t("drawer.drawerTitle");
const editTip = t("drawer.editTip");
const deleteTip = t("drawer.deleteTip");

const drawerStore = useDrawerStore();
const isDrawerOpen = computed(() => drawerStore.isDrawerOpen);
const router = useRouter();
const chatStore = useChatStore();
chatStore.initRouter(router);
const originalTitles = ref<Record<number, string>>({});
const isDeleteModalVisible = ref(false);
const selectedHistory = ref({ title: "", uuid: 0 });

const historiesOrigin = computed(() => chatStore.history);
const histories = computed(() => {
  return historiesOrigin.value.sort((a, b) => {
    return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
  });
});
const drawerClasses = computed(
  () =>
    `fixed z-40 top-0 left-16 h-full bg-base-200 border-r border-slate-300 transition-transform transform ${
      isDrawerOpen.value ? "translate-x-0" : "-translate-x-full"
    }`
);

const toggleDrawer = () => {
  drawerStore.toggleDrawer();
};

const openTopic = (uuid: number) => {
  router.push(`/chat/${uuid}`);
  drawerStore.toggleDrawer();
};

const inputRefs = ref(new Map<number, HTMLInputElement>());

const setRef = (el: HTMLInputElement | null, history: Chat.History) => {
  if (el) {
    inputRefs.value.set(history.uuid, el);
  }
};

const editTitle = (
  { uuid, title }: Chat.History,
  isEdit: boolean,
  event?: Event
) => {
  event?.stopPropagation();
  chatStore.updateHistory(uuid, { isEdit });
  if (isEdit) {
    originalTitles.value[uuid] = title;
    nextTick(() => {
      const input = inputRefs.value.get(uuid);
      if (input) {
        input.focus();
      }
    });
  }
};

const saveEdit = (
  { uuid, title }: Chat.History,
  isEdit: boolean,
  event?: Event
) => {
  event?.stopPropagation();
  const originalTitle = originalTitles.value[uuid];
  if (title !== originalTitle) {
    const updatedAt = new Date().toISOString();
    chatStore.updateHistory(uuid, { title, isEdit, updatedAt });
  } else {
    chatStore.updateHistory(uuid, { isEdit });
  }
  delete originalTitles.value[uuid];
};

const openDeleteModal = ({ title, uuid }: Chat.History, event?: Event) => {
  event?.stopPropagation();
  selectedHistory.value = { title: title, uuid: uuid };
  isDeleteModalVisible.value = true;
};

const handleConfirmDelete = (uuid: number) => {
  if (router.currentRoute.value.path === `/chat/${uuid}`) {
    router.push("/");
    drawerStore.toggleDrawer();
  }
  chatStore.deleteHistory(uuid);
  isDeleteModalVisible.value = false;
};

const handleConfirmDeleteDebounce = debounce(handleConfirmDelete, 500);
</script>
