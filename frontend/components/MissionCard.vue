<template>
  <div class="card w-96 bg-base-100 shadow-xl m-4">
    <figure><img :src="imageUrl" alt="Shoes"/></figure>
    <div class="card-body">
      <h2 class="card-title">{{ missionTitle }}</h2>
      <p>{{ missionDescription }}</p>
      <div class="card-actions justify-center">
        <button class="btn btn-primary">Run mission</button>
      </div>
    </div>
  </div>
</template>

<script>
import {defineComponent} from '@nuxtjs/composition-api'

export default defineComponent({
  props: ['title', 'imageSrc', 'description'],
  setup(props) {
    const missionTitle = props.title
    const imageUrl = props.imageSrc
    const missionDescription = props.description

    return {missionTitle, imageUrl, missionDescription}
  }
})

</script>
