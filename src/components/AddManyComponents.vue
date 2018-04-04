<template>
  <div>
    <div v-for="(entry, index) in entries" :key="index">
      <button 
        @click="onClickRemove(index)" 
        type="button" 
        class="btn btn-primary float-right" 
      >
        <icon name="minus"/>
      </button>
    <component 
      :is="entryComponent"
      v-model="values[index]"
    />
    </div>

    <button 
      @click="onClickAction" 
      type="button" 
      class="btn btn-primary" 
    >
      <icon name="plus"/>
    </button>
    {{values}}
  </div>
</template>

<script>
export default {
  components: {
  },
  props: {
    value: Array,
    entryComponent: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      entries: [],
      values: []
    }
  },
  computed: {
    hasEntryComponent () {
      return this.entryComponent !== undefined
    }
  },
  watch: {
    values: {
      handler (val) {
        this.$emit('input', val)
      },
      deep: true
    }
  },
  methods: {
    onClickAction () {
      this.entries.push(this.entryComponent)
    },

    onClickRemove (index) {
      this.entries.splice(index, 1)
    }
  }
}
</script>

