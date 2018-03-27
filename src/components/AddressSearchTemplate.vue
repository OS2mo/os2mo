<template>
  <div>
    <label>{{ item.location.name }}</label>
  </div>
</template>

<script>
export default {
  props: {
    item: {
      required: true
    }
  }
}
</script>