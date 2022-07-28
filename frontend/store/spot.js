import { defineStore } from 'pinia'

export const useSpot = defineStore('dashboardParameters', {
  state: () => {
    return {
      status: "unknown",
      battery: 0,
      location: "start",
      gauges: 0
    }
  },
  actions: {

  }
})
