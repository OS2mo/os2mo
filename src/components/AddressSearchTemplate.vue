<template>
  <div>
    <label>{{ item.vejnavn }}</label>
  </div>
</template>

<script>
export default {
  props: {
    item: { required: true }
  }
}
</script>