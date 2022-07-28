<template>
  <div class="flex flex-row">
    <div class="w-1/2 p-8">
      <h2 class="text-5xl font-bold">Observation</h2>

      <SpotDataLabels class="mt-8"/>
      <div class="mt-8">
        <div class="grid grid-cols-2 gap-4">
          <CameraStream title="front left" camera-name="frontleft_fisheye_image"/>
          <CameraStream title="front right" camera-name="frontright_fisheye_image"/>
          <CameraStream title="left" camera-name="left_fisheye_image"/>
          <CameraStream title="right" camera-name="right_fisheye_image"/>
          <CameraStream title="back" camera-name="back_fisheye_image"/>
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
