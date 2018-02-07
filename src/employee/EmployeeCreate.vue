<template>
  <b-modal 
    id="employeeCreate" 
    size="lg" 
    hide-footer 
    title="Ny medarbejder"
    ref="employeeCreate"
  >
  <!-- Modal Component -->
    <employee-create-engagement :org="org" v-model="engagement"/>
    {{engagement}}
    <employee-create-association :org="org" v-model="association"/>

    {{association}}

    <div class="float-right">
      <button-submit @click.native="createEmployee"/>
    </div>
  </b-modal>

</template>

<script>
import Organisation from '../api/Organisation'
import Employee from '../api/Employee'
import { EventBus } from '../EventBus'
import ButtonSubmit from '../components/ButtonSubmit'
import EmployeeCreateAssociation from './EmployeeCreateAssociation'
import EmployeeCreateEngagement from './EmployeeCreateEngagement'

export default {
  components: {
    ButtonSubmit,
    EmployeeCreateAssociation,
    EmployeeCreateEngagement
  },
  data () {
    return {
      org: {},
      engagement: {},
      association: {}
    }
  },
  created () {
    this.org = Organisation.getSelectedOrganisation()
  },
  mounted () {
    EventBus.$on('organisation-changed', newOrg => {
      this.org = newOrg
    })
  },
  methods: {
    createEmployee () {
      let vm = this
      let create = []

      create.push(this.engagement)
      // create.push(this.association)

      Employee.createEmployee(this.$route.params.uuid, create)
      .then(response => {
        vm.$refs.employeeCreate.hide()
        console.log(response)
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>