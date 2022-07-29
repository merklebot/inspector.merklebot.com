import {defineStore} from 'pinia'

export const useSpot = defineStore('spotData', {
  state: () => {
    return {
      status: "unknown",
      cameraImages: {},
      battery: null,
      location: "start",
      gauges: 0
    }
  },
  actions: {
    setSpotAnswer(data) {
      if (!data) {
        this.battery = null
        this.cameraImages = {}
        this.status = "unknown"
        return
      }
      this.battery = data.battery
      this.cameraImages = data.camera_images
    },
    setStatus(status) {
      this.status = status
    }
  }
})
