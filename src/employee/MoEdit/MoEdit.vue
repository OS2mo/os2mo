<template>
  <div>
    <button class="btn btn-outline-primary" v-b-modal="'moEdit'+_uid" @click="showModal=true">
      <icon name="edit" />
    </button>

    <b-modal
      :id="'moEdit'+_uid"
      size="lg"
      hide-footer 
      title="Rediger medarbejder"
      :ref="'moEdit'+_uid"
    >
      <employee-create-engagement v-if="showModal && type=='engagement'" v-model="edit" :org="org"/>
      <employee-create-association v-if="showModal && type=='association'" v-model="edit" :org="org"/>
      <employee-create-role v-if="showModal && type=='role'" v-model="edit" :org="org"/>
      <mo-it-system v-if="showModal && type=='it'" v-model="edit" :org="org"/>

      <div class="float-right">
        <button-submit @click.native="editEmployee" :is-loading="isLoading"/>
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
      content: {
        type: Object,
        required: true
      },
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
      this.edit = JSON.parse(JSON.stringify(this.content))
      this.original = JSON.parse(JSON.stringify(this.content))
    },
    methods: {
      editEmployee () {
        let vm = this
        vm.isLoading = true
        let data = [{
          type: 'engagement',
          uuid: this.edit.uuid,
          original: this.original,
          data: this.edit
        }]

        Employee.edit(this.uuid, data)
        .then(response => {
          vm.isLoading = false
          vm.$refs['moEdit' + vm._uid].hide()
        })
      }
    }
  }
</script>
