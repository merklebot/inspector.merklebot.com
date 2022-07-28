<template>
  <div class="flex flex-row">
    <div class="w-1/2 p-8">
      <h2 class="text-5xl font-bold">Observation</h2>

      <div class="mt-8">
        <div class="stats shadow m-2">
          <div class="stat">
            <div class="stat-title">Spot status</div>
            <div class="stat-value text-green-500">Active</div>
          </div>
        </div>
        <div class="stats shadow m-2">

          <div class="stat">
            <div class="stat-title">Battery</div>
            <div class="stat-value">42%</div>
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

      <div class="mt-8">
        <div class="grid grid-cols-2 grid-rows-2 gap-4">
          <CameraStream title="front" url="https://api.merklebot.com/videoserver/video"/>
          <CameraStream title="back" url="https://api.merklebot.com/videoserver/video"/>
          <CameraStream title="left" url="https://api.merklebot.com/videoserver/video"/>
          <CameraStream title="right" url="https://api.merklebot.com/videoserver/video"/>
        </div>
      </div>

    </div>
    <div class="w-1/2 p-8">
      <h2 class="text-5xl font-bold">Control</h2>

      <div class="mt-8">
        <MissionCard title="Mission #0" description="Exploring gauges indicators and shooting photos"
                     image-src="https://i.ibb.co/L04vQyC/photo-2022-07-27-22-18-35.jpg"/>

        <MissionCard title="Mission #1" description="Office stair climbing and pressing button"
                     image-src="https://i.ibb.co/xmjq46S/photo-2022-07-27-22-09-58.jpg"/>


      </div>
    </div>
  </div>
</template>
<script>
import CameraStream from "~/components/CameraStream";

export default {
  components: {CameraStream}
}
</script>
