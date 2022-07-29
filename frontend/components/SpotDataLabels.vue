<template>
  <div>
    <div class="stats shadow m-2">
      <div class="stat">
        <div class="stat-title">Spot status</div>
        <div
          class="stat-value"
          :class="status.color"
        >{{ status.text }}</div>
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
import {computed, defineComponent, onMounted} from '@nuxtjs/composition-api'
import {useSpot} from "~/store/spot";

export default defineComponent({
  setup(props) {
    const spot = useSpot()
    onMounted(() => {
      const connectToSpot = () => {
        try {
          const spotSocket = new WebSocket("wss://api.merklebot.com/oz/spot/spot/state/ws");
          spotSocket.onmessage = (event) => {
            spot.setSpotAnswer(JSON.parse(event.data))
          }
          spotSocket.onopen = () => spot.setStatus("connected")
          spotSocket.onclose = () => {
            spot.setSpotAnswer()
            setTimeout(connectToSpot, 1000)
          }
          spotSocket.onerror = () => spotSocket.close()
        }
        catch {
          setTimeout(connectToSpot, 1000)
        }
      }
      connectToSpot()
    })

    const status = computed(() => {
      switch (spot.status) {
        case "connected":
          return { text: "Connected", color: "text-green-500" }
        case "unknown":
          return { text: "Trying to connect...", color: "text-red-500" }
        default:
          return { text: "Unexpected connection status", color: "text-yellow-500" }
      }
    })

    return {spot, status}
  }
})

</script>
