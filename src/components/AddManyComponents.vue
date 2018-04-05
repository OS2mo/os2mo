<template>
  <div>
    <div v-for="(v, index) in values" :key="index">
      <mo-removable-component 
        :entry-component="entryComponent" 
        v-model="values[index]"
      />
    </div>

    <button @click="add()" type="button" class="btn btn-primary">
      <icon name="plus"/>
    </button>
  </div>
</template>

<script>
import MoRemovableComponent from './MoRemovableComponent'
export default {
  components: {
    MoRemovableComponent
  },
  props: {
    entryComponent: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      values: []
    }
  },
  updated () {
    let data = this.values.filter(value => Object.keys(value).length !== 0)
    this.$emit('input', data)
  },
  mounted () {
    this.add()
  },
  methods: {
    add () {
      this.values.push({})
    }
  }
}
</script>

