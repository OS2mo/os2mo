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
    }
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
  }
}
</script>

<style scoped>
ul {
  list-style-type: none;
  padding: 0;
}
</style>
