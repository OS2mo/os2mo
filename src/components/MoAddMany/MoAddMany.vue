<template>
  <div>
    <h5> 
      <button @click="add()" type="button" class="btn btn-outline-success" style="border:none!important">
        <icon name="plus"/>
      </button>
      {{label}}
    </h5>

    <div v-for="(v, index) in values" :key="index">
      <mo-removable-component 
        :entry-component="entryComponent" 
        :validity-hidden="validityHidden"
        :even="index%2==0"
      />
    </div>

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
    },
    hasInitialEntry: Boolean,
    validityHidden: Boolean,
    label: String
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
    if (this.hasInitialEntry) {
      this.add()
    }
  },
  methods: {
    add () {
      this.values.push({})
    }
  }
}
</script>

<style scoped>
.even {
  background-color: #eee;
}
</style>
