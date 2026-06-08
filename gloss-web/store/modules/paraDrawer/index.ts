import { defineStore } from "pinia";
import { store } from "@/store/helper";

export const useParaDrawerStore = defineStore("para-drawer", {
  state: () => ({
    drawerWidth: 400,
    lastValidWidth: 400
  }),
  actions: {
    setDrawerWidth(width: number) {
      this.drawerWidth = width;
    },
    setLastValidWidth(width: number) {
      this.lastValidWidth = width;
    },
  },
  persist: true,
});

export function useParaDrawerStoreWithOut() {
  return useParaDrawerStore(store);
}
