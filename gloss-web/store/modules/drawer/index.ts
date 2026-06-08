import { defineStore } from 'pinia';
import { store } from '@/store/helper'

export const useDrawerStore = defineStore('drawer', {
  state: () => ({
    isDrawerOpen: false,
  }),
  actions: {
    toggleDrawer() {
      this.isDrawerOpen = !this.isDrawerOpen;
    },
  },
});

export function useDrawerStoreWithOut() {
  return useDrawerStore(store)
}