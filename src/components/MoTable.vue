<template>
  <div>
    <loading v-show="isLoading"/>
    <div v-show="!isLoading">
    <span v-if="!contentAvailable">Intet at vise</span>
    <b-form-checkbox-group v-model="selected">
    <table v-if="contentAvailable" class="table table-striped">
      <thead>
        <tr>
          <th v-if="multiSelect">
             <!-- <b-form-checkbox
              v-model="selectAll"/> -->
          </th>
          <th 
            scope="col" 
            v-for="col in columns" 
            :key="col"
          >
            {{label[col] }}
          </th>
          <th>Startdato</th>
          <th>Slutdato</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr 
          v-for="c in content" 
          v-bind:key="c.uuid"
        >
          <td v-if="multiSelect">
            <b-form-checkbox :value="c"/>
          </td>
          <td v-for="col in columns" :key="col">
            {{ col ? c[col] : c | getProperty('name') }}
          </td>
          <td>
            {{c.validity | getProperty('from') | date}}
          </td>
          <td>
            {{c.validity.to | date}}
          </td>
          <td>
            <mo-entry-modal-base
              action="EDIT"
              :type="type"
              :uuid="editUuid"
              :entry-component="editComponent"
              :content="c"
              :content-type="contentType"
            />
          </td>
        </tr>
      </tbody>
    </table>
      </b-form-checkbox-group>
    </div>
  </div>
</template>

<script>
  import '../filters/GetProperty'
  import '../filters/Date'
  import Loading from './Loading'
  import MoEntryModalBase from './MoEntryModalBase'

  export default {
    components: {
      Loading,
      MoEntryModalBase
    },
    props: {
      content: Array,
      contentType: String,
      columns: Array,
      isLoading: Boolean,
      editComponent: Object,
      editUuid: String,
      multiSelect: Boolean,
      type: {
        type: String,
        required: true
      }
    },
    data () {
      return {
        selectAll: false,
        selected: [],
        label: {
          null: 'Enhedsnavn',
          org_unit: 'Enhedsnavn',
          org_unit_type: 'Enhedstype',
          parent: 'Overenhed',
          job_function: 'Stillingsbetegnelse',
          engagement_type: 'Engagementstype',
          association_type: 'Tilknytningstype',
          role_type: 'Rolle',
          leave_type: 'Orlovstype',
          it_system: 'System',
          user: 'Brugernavn',
          responsibility: 'Lederansvar',
          manager_type: 'Ledertype',
          manager_level: 'Lederniveau',
          address_type: 'Adressetype',
          person: 'Navn',
          pretty_value: 'Værdi'
        }
      }
    },
    computed: {
      contentAvailable () {
        return this.content ? this.content.length > 0 : false
      }
    },
    watch: {
      selected (newVal) {
        this.$emit('selected-changed', newVal)
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  table {
    margin-top: 0;
  }
</style>