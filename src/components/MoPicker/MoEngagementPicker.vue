<template>
  <div class="form-group col">
    <label>{{$tc('shared.engagement', 2)}}</label>
    <mo-loader v-show="isLoading"/>
    <select
      :name="nameId"
      :id="nameId"
      :ref="nameId"
      data-vv-as="Engagementer"
      v-show="!isLoading" 
      class="form-control col" 
      v-model="selected"
      @change="updateSelectedEngagement()"
      :disabled="!employeeDefined"
      v-validate="{required: true}"
    >
      <option disabled>{{label}}</option>
      <option v-for="e in engagements" :key="e.uuid" :value="e">
          {{e.engagement_type.name}}, {{e.org_unit.name}}
      </option>
    </select>
    <span v-show="errors.has(nameId)" class="text-danger">{{ errors.first(nameId) }}</span>
  </div>
</template>

<script>
import Employee from '@/api/Employee'
import MoLoader from '@/components/atoms/MoLoader'

export default {
  name: 'MoEngagementPicker',
  components: {
    MoLoader
  },
  inject: {
    $validator: '$validator'
  },
  props: {
    value: Object,
    employee: {
      type: Object,
      required: true
    },
    required: Boolean
  },
  data () {
    return {
      selected: null,
      engagements: [],
      isLoading: false,
      label: ''
    }
  },
  computed: {
    nameId () {
      return 'engagement-picker-' + this._uid
    },

    isRequired () {
      if (!this.employeeDefined) return false
      return this.required
    },

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
