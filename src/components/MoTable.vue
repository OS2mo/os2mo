<template>
  <div>
    <loading v-show="isLoading"/>
    <div v-show="!isLoading">
    <span v-if="!contentAvailable">Intet at vise</span>
    <table v-if="contentAvailable" class="table table-striped">
      <thead>
        <tr>
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
          <td v-for="col in columns" :key="col">
            {{ c[col] | getProperty('name') }}
          </td>
          <td>
            {{c.validity | getProperty('from') | date}}
          </td>
          <td>
            {{c.validity.to | date}}
          </td>
          <td>
            <component 
              :is="editComponent" 
              type="EDIT"
              :content="c"
              :uuid="editUuid"
            />
          </td>
        </tr>
      </tbody>
    </table>
    </div>
  </div>
</template>

<script>
  import '../filters/GetProperty'
  import '../filters/Date'
  import Loading from './Loading'

  export default {
    components: {
      Loading
    },
    props: {
      content: Array,
      columns: Array,
      isLoading: Boolean,
      editComponent: Object,
      editUuid: String
    },
    data () {
      return {
        label: {
          org_unit: 'Enhed',
          job_function: 'Stillingsbetegnelse',
          engagement_type: 'Engagementstype',
          association_type: 'Tilknytningstype',
          role_type: 'Rolle'
        }
      }
    },
    computed: {
      contentAvailable () {
        return this.content ? this.content.length > 0 : false
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