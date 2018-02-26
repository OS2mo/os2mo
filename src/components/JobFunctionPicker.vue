<template>
  <div class="form-group col">
    <label v-if="!noLabel">{{label}}</label>
    <select 
      name="job-function-picker"
      :data-vv-as="label"
      class="form-control col" 
      v-model="selected"
      @change="updateSelectedJobFunction()"
      v-validate="{ required: true }"
    >
      <option disabled>{{label}}</option>
      <option 
        v-for="jf in jobFunctions" 
        v-bind:key="jf.uuid"
        :value="jf">
          {{jf.name}}
      </option>
    </select>
    <span
      v-show="errors.has('job-function-picker')" 
      class="text-danger"
    >
      {{ errors.first('job-function-picker') }}
    </span>
  </div>
</template>

<script>
import Facet from '../api/Facet'
import Organisation from '../api/Organisation'
import { EventBus } from '../EventBus'

export default {
  name: 'JobFunctionPicker',
  props: {
    value: Object,
    noLabel: Boolean,
    label: {
      type: String,
      default: 'Stillingsbetegnelse'
    }
  },
  data () {
    return {
      selected: {},
      jobFunctions: []
    }
  },
  mounted () {
    EventBus.$on('organisation-changed', () => {
      this.getJobFunctions()
    })
  },
  created () {
    this.getJobFunctions()
    this.selected = this.value
  },
  methods: {
    getJobFunctions () {
      var vm = this
      let org = Organisation.getSelectedOrganisation()
      if (org.uuid === undefined) return
      Facet.jobFunctions(org.uuid)
      .then(response => {
        vm.jobFunctions = response
      })
    },

    updateSelectedJobFunction () {
      this.$emit('input', this.selected)
    }
  }
}
</script>
