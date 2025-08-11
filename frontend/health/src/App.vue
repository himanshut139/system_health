<template>
  <div id="app">
    <h1 style="text-align: center;"> Admin Dashboard </h1>
    <MachineList />
  </div>
</template>

<script>
import MachineList from './components/MachineList.vue'

export default {
  components: {
    MachineList
  }
}
</script>
