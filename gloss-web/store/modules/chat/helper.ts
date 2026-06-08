import { defineStore } from "pinia";

export const useChatState = defineStore({
  id: "chatStorage",
  state: (): Chat.ChatState => ({
    active: null,
    usingContext: false,
    history: [],
    chat: [],
  }),
  actions: {
    getChatState(): Chat.ChatState {
      return {
        active: this.active,
        usingContext: this.usingContext,
        history: this.history,
        chat: this.chat,
      };
    },
    setChatState(newState: Chat.ChatState) {
      this.active = newState.active;
      this.usingContext = newState.usingContext;
      this.history = newState.history;
      this.chat = newState.chat;
    },
  },
  persist: true,
});
