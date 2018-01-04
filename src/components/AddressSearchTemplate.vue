<template>
  <div>
    <span>{{ item.vejnavn }}</span>
  </div>
</template>

<script>
export default {
  props: {
    item: { required: true },
    searchText: { required: true }
  }
}
</script>