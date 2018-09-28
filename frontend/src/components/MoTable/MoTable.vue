<template>
  <div>
    <mo-loader v-show="isLoading"/>
    <div v-show="!isLoading" class="scroll">
    <table v-if="!contentAvailable" class="table">
      <tbody>
      <tr>
        <td>
          <span>Intet at vise</span>
        </td>
      </tr>
      </tbody>
    </table>

    <b-form-checkbox-group v-model="selected">
    <table v-if="contentAvailable" class="table table-striped">
      <thead>
        <tr>
          <th v-if="multiSelect"></th>
          <th 
            scope="col" 
            v-for="(col, index) in columns" 
            :key="index"
          >
            <span class="link" @click="sortData(col.label, open)">
              {{$t('table_headers.'+col.label)}}
              <icon :name="open[col.label] ? 'sort-up' : 'sort-down'"/>
            </span>
          </th>
          <th>
              {{$t('table_headers.start_date')}}
          </th>
          <th>
              {{$t('table_headers.end_date')}}
          </th>
          <th></th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="(c, index) in sortableContent" :key="index">
          <td v-if="multiSelect">
            <b-form-checkbox 
              class="checkbox-employee" 
              data-vv-as="checkbox" 
              :value="c"
            />
          </td>
          <td v-for="(col, index) in columns" :key="index">
            <mo-link 
              :value="c" 
              :column="col.data" 
              :field="col.field"
            />
          </td>
          <td>{{c.validity.from | date}}</td>
          <td>{{c.validity.to | date}}</td>
          <td>         
            <mo-entry-edit-modal 
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
  import '@/filters/GetProperty'
  import '@/filters/Date'
  import MoLoader from '@/components/atoms/MoLoader'
  import MoEntryEditModal from '@/components/MoEntryEditModal'
  import MoLink from '@/components/MoLink'

  export default {
    components: {
      MoLoader,
      MoLink,
      MoEntryEditModal
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
        open: {},
        sortableContent: null
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
      },

      contentAvailable: function () {
        if (!this.sortableContent) {
          this.sortableContent = this.content
        }
      }
    },

    methods: {
      sortData (colName, toggleIcon) {
        if (toggleIcon[colName] === undefined) {
          toggleIcon[colName] = true
        }
        this.sortableContent.sort(function (a, b) {
          let strA = a[colName].name
          let strB = b[colName].name

          if (toggleIcon[colName]) {
            return (strA < strB) ? -1 : (strA > strB) ? 1 : 0
          } else {
            return (strA < strB) ? 1 : (strA > strB) ? -1 : 0
          }
        })
        this.open[colName] = !this.open[colName]
      }
    }
  }
</script>

<style scoped>
  table {
    margin-top: 0;
  }

  .scroll {
    max-height: 55vh;
    overflow-x: hidden;
    overflow-y: auto;
  }

  .link{
    cursor: pointer;
  }
</style>