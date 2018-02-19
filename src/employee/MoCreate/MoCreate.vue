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
      <mo-engagement-entry v-if="showModal && type=='engagement'" v-model="edit" :org="org" :is-valid="isEngagementValid"/>
      <mo-association-entry 
        v-if="showModal && type=='association'"
        :org="org"
        v-model="edit"
      />
      <mo-role-entry v-if="showModal && type=='role'" v-model="edit" :org="org"/>
      <mo-it-system-entry v-if="showModal && type=='it'" v-model="edit" :org="org"/>

      <div class="float-right">
        <button-submit :on-click-action="create" :is-loading="isLoading" :is-disabled="isDisabled"/>
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
      uuid: String,
      type: String
    },
    data () {
      return {
        edit: {},
        original: {},
        org: Object,
        isLoading: false,
        showModal: false,
        valid: {
          engagement: false
        }
      }
    },
    computed: {
      isDisabled () {
        return !this.valid.engagement
      }
    },
    created () {
      this.org = Organisation.getSelectedOrganisation()
    },
    methods: {
      isEngagementValid (val) {
        this.valid.engagement = val
      },

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
