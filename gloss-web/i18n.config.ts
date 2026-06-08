import en from "./lang/en_us.js";
import zh from "./lang/zh_cn.js";

export default defineI18nConfig(() => ({
  locale: 'en',
  legacy: false,
  messages: {
    en,
    zh,
  }
}));
