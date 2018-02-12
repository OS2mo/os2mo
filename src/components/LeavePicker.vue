<template>
  <div class="form-group col">
    <label>Orlovstype</label>
    <select 
      class="form-control col" 
      name="leavetypes"
      v-model="selected"
      @change="updateSelectedLeaveTypes()"
      v-validate="{ required: true }"
    >
      <option disabled>Orlovstype</option>
      <option 
        v-for="lt in leaveTypes" 
        v-bind:key="lt.uuid"
        :value="lt">
          {{lt.name}}
      </option>
    </select>
    <span v-show="errors.has('leavetypes')" class="text-danger">{{ errors.first('leavetypes') }}</span>
  </div>
</template>

<script>
import Facet from '../api/Facet'

export default {
  name: 'LeavePicker',
  props: {
    value: Object,
    org: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      selected: {},
      leaveTypes: []
    }
  },
  watch: {
    org () {
      this.getLeavePicker()
    }
  },
  methods: {
    getLeavePicker () {
      var vm = this
      Facet.leaveTypes(this.org.uuid)
      .then(response => {
        vm.leaveTypes = response
      })
    },

    updateSelectedLeaveTypes () {
      this.$emit('input', this.selected)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>