<template>
  <div class="bg-base-100 shadow-xl">
    <figure><img :src="cameraUrl" alt="Video stream"/></figure>
    <div class="p-2">
      <p class="font-mono">{{ cameraTitle }}</p>
    </div>
  </div>

</template>

<script>
import {defineComponent} from '@nuxtjs/composition-api'

export default defineComponent({
  props: ['title', 'url'],
  setup(props) {
    const cameraTitle = props.title
    const cameraUrl = props.url


    return {cameraTitle, cameraUrl}
  }
})
</script>
