<template>
    <div class="input-group">
      <span class="input-group-addon">
        <icon name="search"/>
      </span>
      <v-autocomplete 
        :items="results"
        :get-label="getLabel" 
        :component-item="template" 
        @update-items="getSearchResults"
        @item-selected="selected"
        @blur="results=[]"
        :auto-select-one-item="false"
        :min-len="2"
        placeholder="Søg"
      />
    </div>
</template>

<script>
  import Search from '../api/Search'
  import Organisation from '../api/Organisation'
  import VAutocomplete from 'v-autocomplete'
  import 'v-autocomplete/dist/v-autocomplete.css'
  import TheSearchBarTemplate from './TheSearchBarTemplate.vue'
  
  export default {
    components: {
      VAutocomplete
    },
    data () {
      return {
        results: [],
        routeName: '',
        template: TheSearchBarTemplate
      }
    },
    watch: {
      '$route' (to) {
        this.getRouteName(to)
      }
    },
    created () {
      this.getRouteName(this.$route)
    },
    methods: {
      getLabel (item) {
        return item.name
      },

      getRouteName (route) {
        if (route.name.indexOf('Organisation') > -1) {
          this.routeName = 'OrganisationDetail'
        }

        if (route.name.indexOf('Employee') > -1) {
          this.routeName = 'EmployeeDetail'
        }
      },

      getSearchResults (query) {
        let vm = this
        let org = Organisation.getSelectedOrganisation()
        if (vm.routeName === 'EmployeeDetail') {
          Search.employees(org.uuid, query)
          .then(response => {
            vm.results = response
          })
        }

        if (vm.routeName === 'OrganisationDetail') {
          Search.organisations(org.uuid, query)
          .then(response => {
            vm.results = response
          })
        }
      },

      selected (item) {
        this.$router.push({name: this.routeName, params: { uuid: item.uuid }})
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  .input-group {
    width: 500px;
  }
</style>