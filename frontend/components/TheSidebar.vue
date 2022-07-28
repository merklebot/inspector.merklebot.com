<template>
  <aside class="border-r-2">
    <ul class="menu w-56">
      <li :class="currentPage === 'control' ? 'bordered' : ''">
        <NuxtLink to="/control">Control panel</NuxtLink>
      </li>
      <li :class="currentPage === 'history' ? 'bordered' : ''">
        <NuxtLink to="/history">Historical data</NuxtLink>
      </li>
      <li class="disabled"><NuxtLink to="/">Planner</NuxtLink></li>
    </ul>
  </aside>
</template>

<script>
import { computed, defineComponent, useRoute } from '@nuxtjs/composition-api'

export default defineComponent({
  setup() {
    const route = useRoute()
    const currentPage = computed(() => route.value.name)

    return { currentPage }
  },
})
</script>
>
