<template>
  <div class="hero h-full w-full">
    <div class="hero-content text-center">
      <div class="w-full">
        <h1 class="text-5xl font-bold">Inspector</h1>
        <p class="py-6">
          MekrleBot Inspector is an application for Boston Dynamics Spot robot
          inspections use case.
        </p>
        <NuxtLink to="control">
          <button class="btn btn-primary">Open Control Panel</button>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'IndexPage',
}
</script>
