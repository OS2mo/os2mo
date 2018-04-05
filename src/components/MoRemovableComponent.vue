<template>
  <div v-if="!removed">
    <button 
      @click="remove()" 
      type="button" 
      class="btn btn-primary float-right" 
    >
      <icon name="minus"/>
    </button>

    <component 
      :is="entryComponent"
      v-model="entryValue"
    />
  </div>
</template>

<script>
export default {
  props: {
    entryComponent: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      entryValue: {},
      removed: false
    }
  },
  updated () {
    this.$emit('input', this.entryValue)
  },
  methods: {
    remove () {
      this.entryValue = {}
      this.removed = true
    }
  }
}
</script>

