<template>
  <div>
    <label>{{ item.name }}</label>
  </div>
</template>

<script>
export default {
  props: {
    item: { required: true }
  }
}
</script>
