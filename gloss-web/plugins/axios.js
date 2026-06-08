import axios from 'axios'
import { defineNuxtPlugin } from '#app'
import { useRuntimeConfig } from '#imports'

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()

  const service = axios.create({
    baseURL: config.public.baseURL,
  })

  return {
    provide: {
      axios: service
    }
  }
})
