<template>
  <div>
    <button class="btn btn-outline-primary" v-b-modal="'moCreate'+_uid" @click="showModal=true">
      <icon name="plus" /> Nyt engagement
    </button>

    <b-modal
      :id="'moCreate'+_uid"
      size="lg"
      hide-footer 
      title="Opret"
      :ref="'moCreate'+_uid"
    >
      <employee-create-engagement v-if="showModal && type=='engagement'" v-model="edit" :org="org"/>
      <employee-create-association v-if="showModal && type=='association'" v-model="edit" :org="org"/>
      <employee-create-role v-if="showModal && type=='role'" v-model="edit" :org="org"/>
      <mo-it-system v-if="showModal && type=='it'" v-model="edit" :org="org"/>

      <div class="float-right">
        <button-submit @click.native="create" :is-loading="isLoading"/>
      </div>
    </b-modal>

  </div>
</template>

<script>
  import Organisation from '../../api/Organisation'
  import Employee from '../../api/Employee'
  import EmployeeCreateEngagement from '../EmployeeCreateEngagement'
  import EmployeeCreateAssociation from '../EmployeeCreateAssociation'
  import EmployeeCreateRole from '../EmployeeCreateRole'
  import MoItSystem from '../MoItSystem/MoItSystem'
  import ButtonSubmit from '../../components/ButtonSubmit'

  export default {
    components: {
      ButtonSubmit,
      EmployeeCreateEngagement,
      EmployeeCreateAssociation,
      EmployeeCreateRole,
      MoItSystem
    },
    props: {
      value: Object,
      uuid: String,
      type: String
    },
    data () {
      return {
        edit: {},
        original: {},
        org: Object,
        isLoading: false,
        showModal: false
      }
    },
    created () {
      this.org = Organisation.getSelectedOrganisation()
    },
    methods: {
      create () {
        let vm = this
        vm.isLoading = true

        Employee.create(this.uuid, [this.edit])
        .then(response => {
          vm.isLoading = false
          vm.$refs['moCreate' + vm._uid].hide()
        })
      }
    }
  }
</script>
