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
      <mo-engagement-entry v-if="showModal && type=='engagement'" v-model="edit" :org="org"/>
      <mo-association-entry v-if="showModal && type=='association'" v-model="edit" :org="org"/>
      <mo-role-entry v-if="showModal && type=='role'" v-model="edit" :org="org"/>
      <mo-it-system-entry v-if="showModal && type=='it'" v-model="edit" :org="org"/>

      <div class="float-right">
        <button-submit :on-click-action="editEmployee" :is-loading="isLoading"/>
      </div>
    </b-modal>

  </div>
</template>

<script>
  import Organisation from '../../api/Organisation'
  import Employee from '../../api/Employee'
  import MoEngagementEntry from '../MoEngagement/MoEngagementEntry'
  import MoAssociationEntry from '../MoAssociation/MoAssociationEntry'
  import MoRoleEntry from '../MoRole/MoRoleEntry'
  import MoItSystemEntry from '../MoItSystem/MoItSystemEntry'
  import ButtonSubmit from '../../components/ButtonSubmit'

  export default {
    components: {
      ButtonSubmit,
      MoEngagementEntry,
      MoAssociationEntry,
      MoRoleEntry,
      MoItSystemEntry
    },
    props: {
      value: Object,
      uuid: {
        type: String,
        required: true
      },
      content: {
        type: Object,
        required: true
      },
      type: {
        type: String,
        required: true
      }
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
