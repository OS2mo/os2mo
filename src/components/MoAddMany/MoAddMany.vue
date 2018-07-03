<template>
  <div>
    <h5 :class="smallButtons ? 'h5-label' : ''"> 
      <button @click="add()" type="button" class="btn btn-outline-success" :class="smallButtons ? 'btn-sm' : ''" style="border:none!important">
        <icon name="plus"/>
      </button>
      {{label}}
    </h5>

    <div v-for="(v, index) in values" :key="index">
      <mo-removable-component 
        :entry-component="entryComponent" 
        :small-buttons="smallButtons"
        :validity-hidden="validityHidden"
        v-model="values[index]"
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
    value: Array,
    entryComponent: {
      type: Object,
      required: true
    },
    hasInitialEntry: Boolean,
    smallButtons: Boolean,
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
    if (this.value) {
      this.values = this.value
    } else {
      if (this.hasInitialEntry) {
        this.add()
      }
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
.h5-label {
  font-size: 1rem;
  font-weight: 400;
}
</style>
