import { defineStore } from "pinia";
import { useChatState } from "./helper";
import { setRouter, getRouter } from "@/utils/router";
import { useNuxtApp } from "#app";

export const useChatStore = defineStore("chat-store", {
  state: (): Chat.ChatState => {
    const chatState = useChatState();
    return {
      active: chatState.active, // 当前激活的聊天
      usingContext: chatState.usingContext, // 是否使用上下文
      history: chatState.history, // 聊天历史记录
      chat: chatState.chat, // 聊天内容
    };
  },

  getters: {
    // 根据当前激活的聊天获取聊天历史记录
    getChatHistoryByCurrentActive(state: Chat.ChatState) {
      const index = state.history.findIndex(
        (item) => item.uuid === state.active
      );
      if (index !== -1) return state.history[index];
      return null;
    },

    // 根据 UUID 获取聊天记录
    getChatByUuid(state: Chat.ChatState) {
      return (uuid?: number) => {
        if (uuid)
          return state.chat.find((item) => item.uuid === uuid)?.data ?? [];
        return (
          state.chat.find((item) => item.uuid === state.active)?.data ?? []
        );
      };
    },

    getHistoryByUuid(state: Chat.ChatState) {
      return (uuid: number) => {
        return state.history.find((item) => item.uuid === uuid);
      };
    },
  },

  actions: {
    // 初始化 router
    initRouter(router: any) {
      setRouter(router);
    },
    // 设置是否使用上下文
    setUsingContext(context: boolean) {
      this.usingContext = context;
      this.recordState();
    },

    // 添加新的聊天历史记录
    addHistory(history: Chat.History, chatData: Chat.Chat[] = []) {
      this.history.unshift(history);
      this.chat.unshift({ uuid: history.uuid, data: chatData });
      this.active = history.uuid;
    },

    // 更新指定 UUID 的聊天历史记录
    updateHistory(uuid: number, edit: Partial<Chat.History>) {
      const index = this.history.findIndex((item) => item.uuid === uuid);
      if (index !== -1) {
        this.history[index] = { ...this.history[index], ...edit };
        this.recordState();
      }
    },

    async deleteHistory(uuid: number) {
      const index = this.history.findIndex((item) => item.uuid === uuid);
      if (index === -1) {
        return; // 未找到目标项
      }

      this.history.splice(index, 1);
      this.chat.splice(index, 1);

      if (this.active === uuid) {
        this.active = null;
        this.reloadRoute(); // 跳转到首页
      } else {
        this.active = null;
      }
    },

    // 设置当前激活的聊天
    async setActive(uuid: number) {
      this.active = uuid;
      return await this.reloadRoute(uuid);
    },

    // 根据 UUID 和索引获取聊天记录
    getChatByUuidAndIndex(uuid: number, index: number) {
      if (!uuid || uuid === 0) {
        if (this.chat.length) return this.chat[0].data[index];
        return null;
      }
      const chatIndex = this.chat.findIndex((item) => item.uuid === uuid);
      if (chatIndex !== -1) return this.chat[chatIndex].data[index];
      return null;
    },

    // 根据 UUID 添加聊天记录
    addChatByUuid(uuid: number, chat: Chat.Chat) {
      const { $i18n } = useNuxtApp();
      if (!uuid || uuid === 0) {
        // 如果没有历史记录，则创建新的历史记录
        if (this.history.length === 0) {
          const uuid = Date.now();
          this.history.push({
            title: chat.text,
            isEdit: false,
            uuid,
            isFirst: true,
            updatedAt: new Date().toISOString(),
            temperature: 0.6,
            contextNum: 0,
            isContextUnlimited: true,
            tableEnhanceOpen: false,
            paragraphNum: 5,
          });
          this.chat.push({ uuid, data: [chat] });
          this.active = uuid;
          this.recordState();
        } else {
          this.chat[0].data.push(chat);
          if (this.history[0].title === $i18n.t("chat.newChatTitle")) {
            this.history[0].title = chat.text;
          }
          this.recordState();
        }
      }

      const index = this.chat.findIndex((item) => item.uuid === uuid);
      if (index !== -1) {
        this.chat[index].data.push(chat);
        if (this.history[index].title === $i18n.t("chat.newChatTitle")) {
          this.history[index].title = chat.text;
        }
        this.recordState();
      }
    },

    // 更新指定 UUID 和索引的聊天记录
    updateChatByUuid(uuid: number, index: number, chat: Chat.Chat) {
      if (!uuid || uuid === 0) {
        if (this.chat.length) {
          this.chat[0].data[index] = chat;
          this.recordState();
        }
        return;
      }

      const chatIndex = this.chat.findIndex((item) => item.uuid === uuid);
      if (chatIndex !== -1) {
        this.chat[chatIndex].data[index] = chat;
        this.recordState();
      }
    },

    // 部分更新指定 UUID 和索引的聊天记录
    updateChatSomeByUuid(
      uuid: number,
      index: number,
      chat: Partial<Chat.Chat>
    ) {
      if (!uuid || uuid === 0) {
        if (this.chat.length) {
          this.chat[0].data[index] = { ...this.chat[0].data[index], ...chat };
          this.recordState();
        }
        return;
      }

      const chatIndex = this.chat.findIndex((item) => item.uuid === uuid);
      if (chatIndex !== -1) {
        this.chat[chatIndex].data[index] = {
          ...this.chat[chatIndex].data[index],
          ...chat,
        };
        this.recordState();
      }
    },

    // 删除指定 UUID 和索引的聊天记录
    deleteChatByUuid(uuid: number, index: number) {
      if (!uuid || uuid === 0) {
        if (this.chat.length) {
          this.chat[0].data.splice(index, 1);
          this.recordState();
        }
        return;
      }

      const chatIndex = this.chat.findIndex((item) => item.uuid === uuid);
      if (chatIndex !== -1) {
        this.chat[chatIndex].data.splice(index, 1);
        this.recordState();
      }
    },

    // 清空指定 UUID 的聊天记录
    clearChatByUuid(uuid: number) {
      if (!uuid || uuid === 0) {
        if (this.chat.length) {
          this.chat[0].data = [];
          this.recordState();
        }
        return;
      }

      const index = this.chat.findIndex((item) => item.uuid === uuid);
      if (index !== -1) {
        this.chat[index].data = [];
        this.recordState();
      }
    },

    // 清空所有聊天历史记录和聊天内容
    clearHistory() {
      this.history = [];
      this.chat = [];
      this.active = null;
      this.usingContext = false;
      this.recordState();
    },

    // 重新加载路由
    async reloadRoute(uuid?: number) {
      this.recordState();
      const router = getRouter();
      // if (router) {
      //   try {
      //     await router.push({ name: "chat-uuid", params: { uuid } });
      //   } catch (error) {
      //     console.error(`Failed to navigate: ${error}`);
      //   }
      // } else {
      //   console.error("Router is not initialized");
      // }
    },

    // 记录当前状态
    recordState() {
      const chatState = useChatState();
      chatState.setChatState(this.$state);
    },
  },
});
