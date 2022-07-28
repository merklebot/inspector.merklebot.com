<template>
  <div class="bg-base-100 shadow-xl">
    <figure><img :src="'data:image/jpeg;base64, '+ spot.cameraImages[camera]" alt="Video stream"/></figure>
    <div class="p-2">
      <p class="font-mono">{{ cameraTitle }}</p>
    </div>
  </div>

</template>

<script>
import {defineComponent} from '@nuxtjs/composition-api'
import {useSpot} from "~/store/spot";

export default defineComponent({

  props: ['title', 'cameraName'],
  setup(props) {
    const spot = useSpot()
    const cameraTitle = props.title
    const camera = props.cameraName


    return {cameraTitle, camera, spot}
  }
})
</script>
