SPDX-FileCopyrightText: 2018-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <ul :class="classes">
    <li v-for="(part, index) in parts" :key="index">
      <a v-if="part.href" v-bind:href="part.href"
         target="_blank"
         link="noopener noreferrer nofollow">
        {{ part.text }}
      </a>

      <router-link v-else-if="part.target" class="link-color" :to="part.target">
        {{ part.text }}
      </router-link>
      <span v-else>
        {{ part.text }}
      </span>
    </li>
  </ul>
</template>

<script>
/**
 * A link component.
 */

export default {
  props: {
    /**
     * Create two-way data bindings with the component.
     */
    value: Object,

    /**
     * Defines a default field name.
     */
    field: {
      type: String,
      default: 'name'
    },

    /**
     * If set, restrict this entry to the given index in an array.
     */
    index: {
      type: Number,
      default: -1
    },

    /**
     * Defines a default column.
     */
    column: {
      type: String,
      default: null
    },

    /**
     * Defines the label used for the column.
     */
    label: {
      type: String,
      default: null
    },
  },

  data () {
    return {
      /**
       * The column_handlers component value.
       * Used to add OrganisationDetail, EmployeeDetail components.
       */
      column_handlers: {
        'org_unit': 'OrganisationDetail',
        'parent': 'OrganisationDetail',
        'person': 'EmployeeDetail'
      }
    }
  },

  computed: {
    /**
     * Returns columns and fields.
     */
    classes () {
      if (this.column && this.field) {
        return [this.column + '-' + this.field]
      } else if (this.column) {
        return [this.column]
      } else if (this.field) {
        return [this.field]
      } else {
        return []
      }
    },

    /**
     * Defines contents, columns and value.
     */
    parts () {
      let contents = this.column ? this.value[this.column] : this.value

      if (this.column === 'address_type' && this.value) {
        let address = this.value['address']

        if (address instanceof Array) {
          contents = address.map(a => a['address_type'])
        } else if (address && address[this.column]) {
          contents = address[this.column]
        } else {
          contents = this.value['address_type']
        }
      }

      if (this.label === 'dynamic_class' && this.value) {
        let entry = this.fetch_entry(this.column)
        if (entry !== null) {
            contents = [{'name': entry['full_name']}]
        }
      }

      if (this.column === 'visibility' && this.value) {
        let address = this.value['address']

        if (address instanceof Array) {
          contents = address.map(a => a['visibility'])
        } else if (address && address[this.column]) {
          contents = address[this.column]
        } else {
          contents = this.value['visibility']
        }
      }

      if (this.column === 'engagement') {
        let engagementName = this.value['engagement']['job_function']['name']
        let orgUnitName = this.value['engagement']['org_unit']['name']
        contents = `${engagementName}, ${orgUnitName}`
      }

      if (!contents) {
        contents = []
      } else if (!(contents instanceof Array)) {
        contents = [contents]
      } else if (this.index >= 0) {
        contents = [contents[this.index]]
      }

      let handler = this.column_handlers[this.column]
      const parts = []
      for (let i = 0; i < contents.length; i++) {
        let c = contents[i]
        let p = {}
        p.text = (this.field ? c[this.field] : c) || '\u2014'
        p.href = c ? c.href : ''
        if (handler && c && c.uuid) {
          p.target = {
            name: handler,
            params: {
              uuid: c.uuid
            }
          }
        }
        parts.push(p)
      }
      return parts
    }
  },

  methods: {
    /**
     * Find the first element in the array fulfilling the predicate
     * @param {Array} arr - Array to search for elements in
     * @param {Function} test - The predicate function to run against each element
     * @param {Any} ctx - Context to be passed through to the predicate
     * @returns {Any} the found element in the list or null
     */
    find(arr, test, ctx) {
      let result = null;
      arr.some(function(el, i) {
        return test.call(ctx, el, i, arr) ? ((result = el), true) : false;
      });
      return result;
    },

    /**
     * Fetch the relevant entry for rendering.
     * @param {String} dynamic - Uuid for the head facet
     * @returns {Any} the found element in the list or null
     */
    fetch_entry(dynamic) {
      // Ensure we have an array
      if (Array.isArray(this.value.dynamic_classes) == false) {
        this.value.dynamic_classes = []
      }
      // Find the correct element if it exists
      return this.find(
        this.value.dynamic_classes,
        item => { return item['top_level_facet']['uuid'] == dynamic}
      )
    }
  }
}
</script>

<style scoped>
ul {
  list-style-type: none;
  padding: 0;
}
</style>
