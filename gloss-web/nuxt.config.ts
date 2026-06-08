// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devServer: {
    port: 3006,
  },
  compatibilityDate: "2024-04-03",
  devtools: { enabled: false },
  css: [
    "~/assets/css/main.css",
    "~/assets/css/highlight.less",
    "katex/dist/katex.min.css",
  ],
  postcss: {
    plugins: {
      tailwindcss: {},
      autoprefixer: {},
    },
  },
  routeRules: {
    "/**": { ssr: false },
  },
  modules: [
    [
      "@pinia/nuxt",
      {
        autoImports: [
          // 自动引入 `defineStore()`
          "defineStore",
          // 自动引入 `defineStore()` 并重命名为 `definePiniaStore()`
          ["defineStore", "definePiniaStore"],
        ],
      },
    ],
    "@pinia-plugin-persistedstate/nuxt",
    "@nuxtjs/i18n",
    "@nuxt/icon",
    "@vueuse/nuxt",
  ],
  icon: {
    clientBundle: {
      icons: [
        "lucide:panel-right-close",
        "lucide:panel-right-open",
        "lucide:share-2",
        "mdi:arrow-down-thin",
        "uil:temperature-empty",
        "material-symbols:timer-off-outline",
        "material-symbols:timer-outline",
        "streamline:interface-text-formatting-paragraph-bullets-points-bullet-align-paragraph-formatting-bullets-text",
        "streamline:interface-layout-border-full-grid-layout-layouts-module",
      ],
      scan: {
        globInclude: ["pages/**/*.vue"],
        globExclude: ["node_modules", "dist"],
      },
      includeCustomCollections: true,
    },
  },
  piniaPersistedstate: {
    storage: "localStorage",
  },
  i18n: {
    locales: [
      { code: "en", name: "English", file: "en_us.js", iso: "en-US" },
      { code: "zh", name: "中文", file: "zh_cn.js", iso: "zh-CN" },
    ],
    strategy: "no_prefix",
    defaultLocale: "en",
    langDir: "lang",
    detectBrowserLanguage: {
      useCookie: true,
      alwaysRedirect: true,
      cookieKey: "i18n_cookie",
      redirectOn: "root",
    },
    vueI18n: "./i18n.config.ts",
  },
  plugins: ["@/plugins/axios.js"],
  runtimeConfig: {
    public: {
      baseURL: process.env.NUXT_GLOB_API_URL,
      paragraphTimeout: process.env.PARAGRAPH_TIMEOUT,
      chatTimeout: process.env.CHAT_TIMEOUT,
    },
  },
});
