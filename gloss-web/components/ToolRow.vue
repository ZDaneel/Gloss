<template>
  <!-- 图标行 -->
  <div class="flex items-center justify-start mt-1 ml-4 space-x-2">
    <button
      :class="buttonClass"
      @click="toggleTemperatureSettings"
      ref="temperatureRef"
      v-bind="showTip && { 'data-tip': temperatureText }"
    >
      <Icon name="uil:temperature-empty" class="w-5 h-5 text-gray-500" />
    </button>
    <Teleport to="body">
      <Popup
        ref="temperaturePopupRef"
        :withSwitch="false"
        :title="temperatureText"
        :titleExplanation="temperatureExplanation"
      >
        <div class="flex items-center justify-between space-x-3">
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            v-model.number="localTemperature"
            class="w-2/3 range range-primary range-sm"
          />
          <input
            type="number"
            min="0"
            max="1"
            step="0.1"
            v-model.number="localTemperature"
            class="w-1/3 input input-sm input-primary"
          />
        </div>
      </Popup>
    </Teleport>
    <button
      :class="buttonClass"
      @click="toggleContextSettings"
      ref="contextSettingsRef"
      v-bind="showTip && { 'data-tip': contextCountText }"
    >
      <Icon
        :name="
          localIsContextUnlimited
            ? 'material-symbols:timer-off-outline'
            : 'material-symbols:timer-outline'
        "
        class="w-5 h-5 text-gray-500"
      />
    </button>
    <Teleport to="body">
      <Popup
        ref="contextSettingsPopupRef"
        :title="contextCountText"
        :titleExplanation="contextCountExplanation"
        :withSwitch="true"
      >
        <PopupWithSwitch
          :rangeMin="0"
          :rangeMax="30"
          :rangeStep="1"
          :rangeValue="localContextCount"
          :isUnlimited="localIsContextUnlimited"
          @update:rangeValue="localContextCount = $event"
          @update:isUnlimited="localIsContextUnlimited = $event"
        />
      </Popup>
    </Teleport>

    <button
      :class="buttonClass"
      @click="toggleParagraphSettings"
      ref="paragraphSettingsRef"
      v-bind="showTip && { 'data-tip': paragraphCountText }"
    >
      <Icon
        name="streamline:interface-text-formatting-paragraph-bullets-points-bullet-align-paragraph-formatting-bullets-text"
        class="w-5 h-5 text-gray-500"
      />
    </button>
    <Teleport to="body">
      <Popup
        ref="paragraphSettingsPopupRef"
        :withSwitch="false"
        :title="paragraphCountText"
        :titleExplanation="paragraphCountExplanation"
      >
        <div class="flex items-center justify-between space-x-3">
          <input
            type="range"
            min="1"
            max="10"
            step="1"
            v-model.number="localParagraphCount"
            class="w-2/3 range range-primary range-sm"
          />
          <input
            type="number"
            min="1"
            max="10"
            step="1"
            v-model.number="localParagraphCount"
            class="w-1/3 input input-sm input-primary"
          />
        </div>
      </Popup>
    </Teleport>
    <!-- 表格增强 -->
    <button
      :class="buttonClass"
      @click="toggleTableSettings"
      ref="tableSettingsRef"
      v-bind="showTip && { 'data-tip': tableSettingsText }"
    >
      <Icon
        name="streamline:interface-layout-border-full-grid-layout-layouts-module"
        class="w-5 h-5 text-gray-500"
      />
    </button>
    <Teleport to="body">
      <Popup
        ref="tableSettingsPopupRef"
        :withSwitch="false"
        :title="tableSettingsText"
        :titleExplanation="tableSettingsExplanation"
      >
        <div class="flex items-center justify-between space-x-3">
          <input
            type="checkbox"
            class="toggle toggle-primary"
            v-model="localTableEnhanceOpen"
          />
          <span class="font-medium text-md whitespace-nowrap">
            {{
              localTableEnhanceOpen
                ? tableEnhanceOpenText
                : tableEnhanceCloseText
            }}
          </span>
        </div>
      </Popup>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineProps, defineEmits, provide } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const temperatureText = computed(() => t("chat.temperature"));
const temperatureExplanation = computed(() => t("chat.temperatureExplanation"));
const contextCountText = computed(() => t("chat.contextCount"));
const contextCountExplanation = computed(() =>
  t("chat.contextCountExplanation")
);
const contextUnlimitedText = computed(() => t("chat.contextUnlimited"));
const paragraphCountText = computed(() => t("chat.paragraphCount"));
const paragraphCountExplanation = computed(() =>
  t("chat.paragraphCountExplanation")
);
const tableSettingsText = computed(() => t("chat.tableSettings"));
const tableSettingsExplanation = computed(() =>
  t("chat.tableSettingsExplanation")
);
const tableEnhanceOpenText = computed(() => t("chat.tableEnhanceOpen"));
const tableEnhanceCloseText = computed(() => t("chat.tableEnhanceClose"));

const buttonClass =
  "p-1 pb-0 text-gray-500 transition duration-150 ease-in-out transform rounded-lg tooltip tooltip-bottom hover:text-gray-700 hover:bg-neutral-content hover:scale-105 active:scale-95";

const temperatureRef = ref();
const contextSettingsRef = ref();
const paragraphSettingsRef = ref();
const tableSettingsRef = ref();

const props = defineProps({
  showTip: Boolean,
  temperature: Number,
  contextCount: Number,
  isContextUnlimited: Boolean,
  paragraphCount: Number,
  tableEnhanceOpen: Boolean,
});

const emit = defineEmits([
  "update:temperature",
  "update:contextCount",
  "update:isContextUnlimited",
  "update:paragraphCount",
  "update:tableEnhanceOpen",
]);

const localTemperature = ref(props.temperature);
const localParagraphCount = ref(props.paragraphCount);
const localContextCount = ref(props.contextCount);
const localIsContextUnlimited = ref(props.isContextUnlimited);
const localTableEnhanceOpen = ref(props.tableEnhanceOpen);

const temperaturePopupRef = ref<any>(null);
const toggleTemperatureSettings = () => {
  temperaturePopupRef.value?.toggle(temperatureRef);
};

const contextSettingsPopupRef = ref<any>(null);
const toggleContextSettings = () => {
  contextSettingsPopupRef.value?.toggle(contextSettingsRef);
};

const paragraphSettingsPopupRef = ref<any>(null);
const toggleParagraphSettings = () => {
  paragraphSettingsPopupRef.value?.toggle(paragraphSettingsRef);
};

const tableSettingsPopupRef = ref<any>(null);
const toggleTableSettings = () => {
  tableSettingsPopupRef.value?.toggle(tableSettingsRef);
};

watch(localTemperature, (newValue) => {
  emit("update:temperature", newValue);
});

watch(localParagraphCount, (newValue) => {
  emit("update:paragraphCount", newValue);
});

watch(localContextCount, (newValue) => {
  emit("update:contextCount", newValue);
});

watch(localIsContextUnlimited, (newValue) => {
  emit("update:isContextUnlimited", newValue);
});

watch(localTableEnhanceOpen, (newValue) => {
  emit("update:tableEnhanceOpen", newValue);
});
</script>
