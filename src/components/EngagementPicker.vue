<template>
  <div class="form-group col">
    <label>{{label}}</label>
    <loading v-show="isLoading"/>
    <select
      v-show="!isLoading" 
      class="form-control col" 
      v-model="selected"
      @change="updateSelectedEngagement()"
      :disabled="!employeeDefined">
      <option disabled>{{label}}</option>
      <option 
        v-for="e in engagements" 
        v-bind:key="e.uuid"
        :value="e">
          {{e.engagement_type.name}}, {{e.org_unit.name}}
      </option>
    </select>
  </div>
</template>

<script>
import Employee from '../api/Employee'
import Loading from './Loading'
import { EventBus } from '../EventBus'

export default {
  name: 'EngagementPicker',
  components: {
    Loading
  },
  props: {
    value: Object,
    employee: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      label: 'Engagementer',
      selected: {},
      engagements: [],
      isLoading: false
    }
  },
  computed: {
    employeeDefined () {
      for (let key in this.employee) {
        if (this.employee.hasOwnProperty(key)) {
          return true
        }
      }
      return false
    }
  },
  watch: {
    employee () {
      this.getEngagements()
    }
  },
  mounted () {
    EventBus.$on('employee-changed', () => {
      this.getEngagements()
    })
  },
  beforeDestroy () {
    EventBus.$off(['employee-changed'])
  },
  methods: {
    getEngagements () {
      if (this.employeeDefined) {
        let vm = this
        vm.isLoading = true
        Employee.getEngagementDetails(this.employee.uuid)
          .then(response => {
            vm.isLoading = false
            vm.engagements = response
          })
      }
    },

    updateSelectedEngagement () {
      this.$emit('input', this.selected)
    }
  }
}
</script>
