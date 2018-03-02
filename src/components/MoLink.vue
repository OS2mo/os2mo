<template>
  <a v-if="href" v-bind:href="href"
     target="_blank"
     link="noopener noreferrer nofollow">
    {{text}}
  </a>
  <router-link v-else-if="target" class="link-color" :to="target">
    {{text}}
  </router-link>
  <span v-else>
    {{text}}
  </span>
</template>

<script>
  export default {
    props: {
      value: Object,
      field: {
        type: String,
        default: () => 'name'
      },
      column: {
        type: String,
        default: () => null
      }
    },
    data() {
      return {
        column_handlers: {
          'org_unit': 'OrganisationDetail',
          'parent': 'OrganisationDetail',
          'person': 'EmployeeDetail'
        }
      }
    },
    computed: {
      target () {
        let handler = this.column_handlers[this.column]

        if (handler && this.contents && this.contents.uuid) {
          return {
            name: handler,
            params: {
              uuid: this.contents.uuid
            }
          }
        }
      },

      href () {
        return this.contents.href
      },

      contents () {
        return this.column ? this.value[this.column] : this.value
      },

      text () {
        return (this.contents && this.contents[this.field]) || '\u2014'
      }
    }
  }
</script>
