<template>
  <div class="form-group col">
    <label v-if="!noLabel">{{label}}</label>
    <select 
      name="leave-picker"
      :data-vv-as="label"
      class="form-control col" 
      v-model="selected"
      @change="updateSelectedLeaveType()"
      v-validate="{ required: true }"
    >
      <option disabled>{{label}}</option>
      <option 
        v-for="lt in leaveTypes" 
        v-bind:key="lt.uuid"
        :value="lt">
          {{lt.name}}
      </option>
    </select>
    <span
      v-show="errors.has('leave-picker')" 
      class="text-danger"
    >
      {{ errors.first('leave-picker') }}
    </span>
  </div>
</template>

<script>
import Facet from '../api/Facet'
import Organisation from '../api/Organisation'
import { EventBus } from '../EventBus'

export default {
  name: 'LeavePicker',
  props: {
    value: Object,
    noLabel: Boolean,
    label: {
      type: String,
      default: 'Orlovstype'
    }
  },
  data () {
    return {
      selected: {},
      leaveTypes: []
    }
  },
  mounted () {
    EventBus.$on('organisation-changed', () => {
      this.getLeaveTypes()
    })
  },
  created () {
    this.getLeaveTypes()
    this.selected = this.value
  },
  methods: {
    getLeaveTypes () {
      var vm = this
      let org = Organisation.getSelectedOrganisation()
      if (org.uuid === undefined) return
      Facet.leaveTypes(org.uuid)
      .then(response => {
        vm.leaveTypes = response
      })
    },

    updateSelectedLeaveType () {
      this.$emit('input', this.selected)
    }
  }
}
</script>
