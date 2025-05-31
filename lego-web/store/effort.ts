import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { Update } from "./voice/voice-client";

export interface EffortStore {
  efforts: Update[];
  addEffortList: (updates: Update[]) => void;
  addEffort: (update: Update) => void;
  removeEffort: (index: number) => void;
  clearEfforts: () => void;
}

export const useEffortStore = create<EffortStore>()(
  persist(
    (set) => ({
      efforts: [],
      addEffortList: (updates) =>
        set((state) => ({ efforts: [...state.efforts, ...updates] })),
      addEffort: (update) =>
        set((state) => ({ efforts: [...state.efforts, update] })),
      removeEffort: (index) =>
        set((state) => ({
          efforts: state.efforts.filter((_, i) => i !== index),
        })),
      clearEfforts: () => set({ efforts: [] }),
    }),
    {
      name: "effort-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);