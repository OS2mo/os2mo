SPDX-FileCopyrightText: 2018-2021 Magenta ApS SPDX-License-Identifier: MPL-2.0

<template>
  <section class="datagrid-container">
    <header class="datagrid-header">
      <div>
        <slot name="datagrid-header"></slot>
      </div>

      <form class="datagrid-filter" @submit.prevent>
        <!-- TODO: Add download single file as CSV -->
        <label
          :for="`filter-field-${componentId}`"
          title="Find i liste"
          class="form-label"
        >
          <span class="sr-only">{{ $t("common.find_in_list") }}</span>
        </label>
        <input
          type="search"
          class="form-control"
          name="query"
          v-model="filterKey"
          :id="`filter-field-${componentId}`"
          :placeholder="$t('common.find_in_list')"
          :disabled="dataList.length < 1 ? true : false"
        />
      </form>
    </header>

    <div class="datagrid-table-wrapper">
      <table class="datagrid table" v-if="filteredData.length > 0">
        <thead>
          <tr>
            <th
              v-for="c in dataFields"
              :key="c.name"
              @click="sortBy(c.name)"
              :class="`datagrid-filter-th ${c.class ? c.class : ''}${
                sortKey === c.name ? ' active' : ''
              }`"
            >
              <span
                v-if="c.name"
                class="datagrid-th-arrow"
                :class="sortOrders[c.name] > 0 ? 'asc' : 'dsc'"
              ></span>
              <span class="datagrid-th-title">{{ c.name }}</span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in filteredData" :key="d.id" :class="`datagrid-r-${d.id}`">
            <template v-for="f in dataFields">
              <td :key="f.name" :title="d[f.name]">
                {{ d[f.name] }}
              </td>
            </template>
          </tr>
          <slot name="datagrid-table-footer"></slot>
        </tbody>
      </table>
    </div>

    <slot name="datagrid-footer"></slot>

    <p v-if="filteredData.length < 1 && filterKey">
      {{ $t("alerts.no_search_results") }}
    </p>
  </section>
</template>

<script>
import Service from "@/api/HttpCommon"

export default {
  props: {
    dataList: [Array, Boolean],
    dataFields: Array,
  },
  data: function () {
    let sortOrders = {}
    for (let f of this.dataFields) {
      sortOrders[f.name] = -1
    }
    return {
      componentId: null,
      sortKey: "",
      sortOrders: sortOrders,
      filterKey: "",
    }
  },
  computed: {
    filteredData: function () {
      var sortKey = this.sortKey
      var filterKey = this.filterKey && this.filterKey.toLowerCase()
      var order = this.sortOrders[sortKey] || 1
      var list = this.dataList
      if (filterKey) {
        list = list.filter((row) => {
          let fewer_keys = Object.keys(row)
          fewer_keys = fewer_keys.filter((key) => {
            for (let field of this.dataFields) {
              if (field.name === key) {
                // Add "&& field.searchable !== false" if you want to exclude some columns in searches
                return key
              }
            }
          })
          return fewer_keys.some(function (key) {
            return String(row[key]).toLowerCase().indexOf(filterKey) > -1
          })
        })
      }
      if (sortKey) {
        list = list.slice().sort(function (a, b) {
          a = a[sortKey]
          b = b[sortKey]
          return (a === b ? 0 : a > b ? 1 : -1) * order
        })
      }
      return list
    },
  },
  methods: {
    sortBy: function (key) {
      if (key) {
        this.sortKey = key
        this.sortOrders[key] = this.sortOrders[key] * -1
      }
    },
  },
  mounted: function () {
    this.componentId = this._uid
  },
}
</script>

<style>
.datagrid-container {
  margin: 0 0 1rem;
}

.datagrid-table-wrapper {
  overflow: auto;
}

.datagrid {
  margin-top: 0;
}

.datagrid th {
  background-color: var(--light);
  color: var(--gray);
  cursor: pointer;
  user-select: none;
  vertical-align: middle;
  font-weight: normal;
  font-size: 0.85rem;
  padding-left: 0;
}

.datagrid-filter-th {
  padding-left: 0;
  white-space: nowrap;
}

.datagrid th.active {
  color: var(--dark);
}

.datagrid th.active .datagrid-th-arrow {
  opacity: 1;
}

.datagrid .datagrid-th-arrow {
  display: inline-block;
  vertical-align: middle;
  width: 0;
  height: 0;
  margin: 0 0.25rem 0 0.5rem;
  opacity: 0.5;
}

.datagrid .datagrid-th-arrow.asc {
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 4px solid var(--dark);
}

.datagrid .datagrid-th-arrow.dsc {
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-bottom: 4px solid var(--dark);
}

.datagrid td {
  vertical-align: middle;
  padding: 0.5rem;
}

.datagrid td.datagrid-action {
  padding: 0;
}

.datagrid td.datagrid-action > a:link,
.datagrid td.datagrid-action > a:visited,
.datagrid button.datagrid-action-btn {
  display: block;
  border: none;
  padding: 0.75rem;
  background-color: transparent;
  text-align: left;
  transition: transform 0.33s;
  box-shadow: none;
  font-size: 1rem;
  height: auto;
  margin: 0;
}

.datagrid td.datagrid-action > a:hover,
.datagrid td.datagrid-action > a:active,
.datagrid td.datagrid-action > a:focus,
.datagrid button.datagrid-action-btn:hover,
.datagrid button.datagrid-action-btn:active,
.datagrid button.datagrid-action-btn:focus {
  transform: translate(0.5rem, 0);
  color: var(--primary);
}

.datagrid-header {
  display: grid;
  grid-template-columns: auto auto;
  margin: 1rem 0;
}

.datagrid-filter {
  background-color: transparent;
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
  justify-content: flex-end;
  padding: 0.5rem 0;
  margin: 0;
}

.datagrid-filter label {
  margin: 0 0.5rem 0 0;
}

.datagrid-filter input {
  width: 8.5rem;
  padding: 0.125rem 0.5rem;
}
</style>
