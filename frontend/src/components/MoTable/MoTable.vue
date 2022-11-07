SPDX-FileCopyrightText: 2018-2020 Magenta ApS SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <mo-loader v-show="isLoading" />
    <div v-show="!isLoading" class="scroll">
      <table v-if="!contentAvailable" class="table">
        <tbody>
          <tr>
            <td>
              <span>{{ $t("common.nothing_to_show") }}</span>
            </td>
          </tr>
        </tbody>
      </table>

      <b-form-checkbox-group v-model="selected">
        <table v-if="contentAvailable" class="table table-striped">
          <thead>
            <tr>
              <th v-if="multiSelect"></th>
              <th scope="col" v-for="(col, index) in columns" :key="index">
                <span @click="sortData(col.label, open)" v-if="hasSorting(col)">
                  {{ prepareLabel(col) }}
                  <icon
                    class="link"
                    :name="open[col.label] ? 'sort-up' : 'sort-down'"
                  />
                </span>
                <span v-if="!hasSorting(col)">
                  {{ prepareLabel(col) }}
                </span>
              </th>
              <th class="date-width">
                <span @click="sortDate(open.from, 'from')">
                  {{ $t("table_headers.start_date") }}
                  <icon class="link" :name="open.from ? 'sort-up' : 'sort-down'" />
                </span>
              </th>
              <th class="date-width">
                <span @click="sortDate(open.to, 'to')">
                  {{ $t("table_headers.end_date") }}
                  <icon class="link" :name="open.to ? 'sort-up' : 'sort-down'" />
                </span>
              </th>
              <th class="table-actions" v-if="showEditableHeader && editComponent"></th>
              <th
                class="table-actions"
                v-if="showEditableHeader && isDeletable && editComponent"
              ></th>
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
              <td
                class="column-data"
                v-for="(col, index) in columns"
                :key="index"
                :class="'column-' + col.data"
              >
                <mo-link
                  :value="c"
                  :label="col.label"
                  :column="col.data"
                  :field="col.field"
                  :index="col.index"
                />
              </td>
              <td class="column-from">{{ c.validity.from | date }}</td>
              <td class="column-to">{{ c.validity.to | date }}</td>
              <td class="column-buttons">
                <mo-entry-terminate-modal
                  v-if="isEditable(c) && isDeletable && editComponent"
                  class="terminate-entry"
                  :type="contentType"
                  :content="c"
                  @submit="$emit('update')"
                />
                <mo-entry-edit-modal
                  v-if="isEditable(c) && editComponent"
                  class="edit-entry"
                  :type="type"
                  :uuid="editUuid"
                  :entry-component="editComponent"
                  :content="c"
                  :content-type="contentType"
                  @submit="$emit('update')"
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

import "@/filters/Date"
import MoLoader from "@/components/atoms/MoLoader"
import MoEntryEditModal from "@/components/MoEntryEditModal"
import MoEntryTerminateModal from "@/components/MoEntryTerminateModal"
import MoLink from "@/components/MoLink"
import bFormCheckbox from "bootstrap-vue/es/components/form-checkbox/form-checkbox"
import bFormCheckboxGroup from "bootstrap-vue/es/components/form-checkbox/form-checkbox-group"
import { has_translation_prefix, translate_prefixed } from "../../i18n"

export default {
  components: {
    MoLoader,
    MoLink,
    MoEntryEditModal,
    MoEntryTerminateModal,
    "b-form-checkbox": bFormCheckbox,
    "b-form-checkbox-group": bFormCheckboxGroup,
  },

  props: {
    /**
     * @model
     */
    value: Array,

    /**
     * Defines content.
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
     * Defines the editComponent.
     */
    editComponent: Object,

    /**
     * Defines the UUID of the owning element, i.e. user or unit.
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
      required: true,
    },
  },

  data() {
    return {
      /**
       * The selectAll, selected, open, sortableContent component value.
       * Used to detect changes and restore the value.
       */
      selectAll: false,
      selected: [],
      open: {},
      sortableContent: null,
      isLoading: true,
      showEditableHeader: false,
    }
  },

  computed: {
    /**
     * If content is available, get content.
     */
    contentAvailable() {
      return this.content ? this.content.length > 0 : false
    },

    isDeletable() {
      switch (this.contentType) {
        case "employee":
          return false
        case "org_unit":
          return false
        case "related":
          return false
        default:
          return true
      }
    },
  },

  watch: {
    /**
     * Whenever selected change, update newVal.
     */
    selected(newVal) {
      this.$emit("input", newVal)
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
    content() {
      this.sortableContent = this.content
      this.isLoading = false
    },

    /**
     * Whenever sortableContent change, apply translations.
     */
    sortableContent() {
      this.sortableContent.forEach((element) => {
        for (let property in element) {
          let prop = element[property]
          if (
            prop &&
            prop["name"] &&
            (typeof prop["name"] === "string" || prop["name"] instanceof String)
          ) {
            const prop_name = prop["name"]
            if (has_translation_prefix(prop_name)) {
              prop["name"] = translate_prefixed("table_values", prop_name)
            }
          }
        }
      })
    },

    deep: true,
  },

  methods: {
    /**
     * Determine whether a specific row is editable or not
     */
    isEditable(content) {
      if (content.inherited) {
        this.showEditableHeader = !content.inherited
        return !content.inherited
      }
      return true
    },

    /**
     * Prepare the label for presentation.
     */
    prepareLabel(col) {
      if (col.label_function) {
        return col.label_function()
      }
      return this.$t(`table_headers.${col.label}`)
    },

    /**
     * Columns that not contain sorting.
     */
    hasSorting(col) {
      if (this.contentType === "address") {
        return col.data === "address_type"
      }
      if (this.contentType === "it") {
        return false
      }
      if (this.contentType === "engagement" && this.type === "ORG_UNIT") {
        return col.data !== "org_unit"
      }
      if (this.contentType === "association" && this.type === "ORG_UNIT") {
        return (
          col.data !== "org_unit" &&
          col.data !== "address" &&
          col.data !== "address_type"
        )
      }
      if (this.contentType === "manager") {
        return (
          col.data !== "responsibility" &&
          col.data !== "address" &&
          col.data !== "address_type" &&
          col.data !== "person"
        )
      }
      return (
        (col.data || col.label === "org_unit") &&
        col.data !== "address" &&
        col.data !== "address_type"
      )
    },

    /**
     * Sort data in columns, including default for empty values.
     */
    sortData(colName, toggleIcon) {
      if (toggleIcon[colName] === undefined) {
        toggleIcon[colName] = true
      }
      this.sortableContent.sort(function (a, b) {
        let strA = ""
        let strB = ""
        try {
          strA = a[colName].name
        } catch (e) {}
        try {
          strB = b[colName].name
        } catch (e) {}

        if (toggleIcon[colName]) {
          return strA < strB ? -1 : strA > strB ? 1 : 0
        } else {
          return strA < strB ? 1 : strA > strB ? -1 : 0
        }
      })
      this.open[colName] = !this.open[colName]
    },

    /**
     * Sort dates in columns.
     */
    sortDate(toggleIcon, date) {
      this.sortableContent.sort(function (a, b) {
        let dateA = new Date(a.validity[date])
        let dateB = new Date(b.validity[date])

        if (toggleIcon) {
          return dateA < dateB ? -1 : dateA > dateB ? 1 : 0
        } else {
          return dateA < dateB ? 1 : dateA > dateB ? -1 : 0
        }
      })
      this.open[date] = !this.open[date]
    },
  },
}
</script>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 0;
}

/* IE11 needs a table width in pixels */
/* This IE-specific media query is only read by IE11 */
@media screen and (-ms-high-contrast: active), (-ms-high-contrast: none) {
  table {
    max-width: 768px;
  }
}

th,
td {
  width: 1%;
  text-align: left;
  padding: 0.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
}

.scroll {
  overflow: auto;
}

.link {
  cursor: pointer;
  margin-top: -10px;
}

.column-data {
  min-width: 9rem;
  max-width: 12rem;
}

.column-from {
  min-width: 7rem;
  max-width: 7rem;
}

.column-to {
  min-width: 7rem;
  max-width: 7rem;
}

.column-buttons {
  min-width: 7rem;
  max-width: 7rem;
  margin-right: 2px;
}
.terminate-entry {
  float: right;
  margin-top: 2px;
}
.edit-entry {
  float: right;
  margin-right: 5px;
  margin-top: 2px;
}
</style>
