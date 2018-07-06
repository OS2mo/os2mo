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
  export default {
    props: {
      value: Object,
      field: {
        type: String,
        default: 'name'
      },
      column: {
        type: String,
        default: null
      }
    },
    data () {
      return {
        column_handlers: {
          'org_unit': 'OrganisationDetail',
          'parent': 'OrganisationDetail',
          'person': 'EmployeeDetail'
        }
      }
    },
    computed: {
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

      parts () {
        let contents = this.column ? this.value[this.column] : this.value

        if (this.column === 'address_type' && this.value) {
          contents = this.value['address']
            ? this.value['address'][this.column]
            : this.value['address_type']
        }

        if (!contents) {
          contents = []
        } else if (!(contents instanceof Array)) {
          contents = [contents]
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
