<template>
  <div>
    <div class="stats shadow m-2">
      <div class="stat">
        <div class="stat-title">Spot status</div>
        <div class="stat-value text-green-500">Active</div>
      </div>
    </div>
    <div class="stats shadow m-2">

      <div class="stat">
        <div class="stat-title">Battery</div>
        <div class="stat-value">{{ spot.battery }}%</div>
      </div>

      <div class="stat">
        <div class="stat-title">Location</div>
        <div class="stat-value">Waypoint 1</div>
      </div>

      <div class="stat">
        <div class="stat-title">Gauges captured</div>
        <div class="stat-value">7</div>
      </div>
    </div>
  </div>

</template>

<script>
import {defineComponent, onMounted} from '@nuxtjs/composition-api'
import {useSpot} from "~/store/spot";

export default defineComponent({
  setup(props) {
    const spot = useSpot()
    onMounted(() => {
      const spotSocket = new WebSocket("wss://api.merklebot.com/oz/spot/spot/state/ws");
      spotSocket.onmessage = (event) => {
        spot.setSpotAnswer(JSON.parse(event.data))
      }
    })


    return {spot}
  }
})

</script>
