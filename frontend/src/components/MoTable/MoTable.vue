<template>
  <div>
    <mo-loader v-show="isLoading"/>
    <div v-show="!isLoading" class="scroll">
    <table v-if="!contentAvailable" class="table">
      <tbody>
      <tr>
        <td>
          <span>{{$t('common.nothing_to_show')}}</span>
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
            <span class="link" @click="sortData(col.label, open)" v-if="hasSorting(col)">
              {{$t('table_headers.'+col.label)}}
              <icon :name="open[col.label] ? 'sort-up' : 'sort-down'"/>
            </span>
            <span v-if="!hasSorting(col)">
              {{$t('table_headers.'+col.label)}}
            </span>
          </th>
          <th>
            <span class="link" @click="sortDate(open.from, 'from')">
              {{$t('table_headers.start_date')}}
              <icon :name="open.from ? 'sort-up' : 'sort-down'"/>
            </span>
          </th>
          <th>
            <span class="link" @click="sortDate(open.to, 'to')">
              {{$t('table_headers.end_date')}}
              <icon :name="open.to ? 'sort-up' : 'sort-down'"/>
            </span>
          </th>
          <th></th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="(c, index) in content" :key="index">
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
/**
   * A table component.
   */

import '@/filters/GetProperty'
import '@/filters/Date'
import MoLoader from '@/components/atoms/MoLoader'
import MoEntryEditModal from '@/components/MoEntryEditModal'
import MoLink from '@/components/MoLink'
import bFormCheckbox from 'bootstrap-vue/es/components/form-checkbox/form-checkbox'
import bFormCheckboxGroup from 'bootstrap-vue/es/components/form-checkbox/form-checkbox-group'

export default {
  components: {
    MoLoader,
    MoLink,
    MoEntryEditModal,
    'b-form-checkbox': bFormCheckbox,
    'b-form-checkbox-group': bFormCheckboxGroup
  },

  props: {
    /**
       * @model
       */
    value: Array,
    /**
       * Defines a content.
       */
    content: Array,

    /**
       * Defines a contentType.
       */
    contentType: String,

    /**
       * Defines columns.
       */
    columns: Array,

    /**
       * This boolean property defines the loading.
       */
    isLoading: Boolean,

    /**
       * Defines the editComponent.
       */
    editComponent: Object,

    /**
       * Defines the editUuid.
       */
    editUuid: String,

    /**
       * This boolean property defines the multiSelect
       */
    multiSelect: Boolean,

    /**
       * Defines a required type.
       */
    type: {
      type: String,
      required: true
    }
  },

  data () {
    return {
      /**
       * The selectAll, selected, open, sortableContent component value.
       * Used to detect changes and restore the value.
       */
      selectAll: false,
      selected: [],
      open: {},
      sortableContent: null
    }
  },

  computed: {
    /**
       * If content is available, get content.
       */
    contentAvailable () {
      return this.content ? this.content.length > 0 : false
    }
  },

  watch: {
    /**
       * Whenever selected change, update newVal.
       */
    selected (newVal) {
      this.$emit('input', newVal)
    },

    /**
       * Whenever contentAvailable change, set sortableContent to content.
       */
    contentAvailable: function () {
      if (!this.sortableContent) {
        this.sortableContent = this.content
      }
    },

    /**
       * Whenever content change, set sortableContent to content.
       */
    content () {
      this.sortableContent = this.content
    },
    deep: true
  },

  methods: {
    /**
       * Columns that not contain sorting.
       */
    hasSorting (col) {
      if (this.contentType === 'address') {
        return col.data === 'address_type'
      }
      if (this.contentType === 'it') {
        return false
      }
      if (this.contentType === 'engagement' && this.type === 'ORG_UNIT') {
        return col.data !== 'org_unit'
      }
      if (this.contentType === 'association' && this.type === 'ORG_UNIT') {
        return col.data !== 'org_unit' &&
          col.data !== 'address' &&
          col.data !== 'address_type'
      }
      if (this.contentType === 'manager') {
        return col.data !== 'responsibility' &&
          col.data !== 'address' &&
          col.data !== 'address_type' &&
          col.data !== 'person'
      }
      return (col.data || col.label === 'org_unit') &&
        col.data !== 'address' &&
        col.data !== 'address_type'
    },

    /**
       * Sort data in columns.
       */
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
    },

    /**
       * Sort dates in columns.
       */
    sortDate (toggleIcon, date) {
      this.sortableContent.sort(function (a, b) {
        let dateA = new Date(a.validity[date])
        let dateB = new Date(b.validity[date])

        if (toggleIcon) {
          return (dateA < dateB) ? -1 : (dateA > dateB) ? 1 : 0
        } else {
          return (dateA < dateB) ? 1 : (dateA > dateB) ? -1 : 0
        }
      })
      this.open[date] = !this.open[date]
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
