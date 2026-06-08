import { NuxtPage } from '#build/components';
<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup>
import { onMounted } from "vue";
import { useHead } from "@unhead/vue";

onMounted(() => {
  const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");

  const initialTheme = prefersDarkScheme.matches ? "dark" : "light";
  useHead({
    link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
  });

  const storedTheme = localStorage.getItem("theme");
  if (storedTheme) {
    document.documentElement.setAttribute("data-theme", storedTheme);
  } else {
    document.documentElement.setAttribute("data-theme", initialTheme);
    localStorage.setItem("theme", initialTheme);
  }
});
</script>
