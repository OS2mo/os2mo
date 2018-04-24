<template>
    <div class="input-group">
      <span class="input-group-addon">
        <icon name="search"/>
      </span>
      <v-autocomplete 
      :items="items" 
      v-model="item" 
      :get-label="getLabel" 
      :component-item='template' 
      @item-selected="selected"
      @update-items="updateItems"
      :auto-select-one-item="false"
      :min-len="2"
      placeholder="Søg"/>
    </div>
</template>

<script>
  import Search from '@/api/Search'
  import VAutocomplete from 'v-autocomplete'
  import 'v-autocomplete/dist/v-autocomplete.css'
  import TheSearchBarTemplate from './TheSearchBarTemplate.vue'
  
  export default {
    components: {
      VAutocomplete
    },
    data () {
      return {
        item: null,
        items: [],
        routeName: '',
        template: TheSearchBarTemplate,
        noItem: [{name: 'Ingen resultater matcher din søgning'}]
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
        return item ? item.name : null
      },

      getRouteName (route) {
        if (route.name.indexOf('Organisation') > -1) {
          this.routeName = 'OrganisationDetail'
        }

        if (route.name.indexOf('Employee') > -1) {
          this.routeName = 'EmployeeDetail'
        }
      },

      updateItems (query) {
        let vm = this
        vm.items = []
        let org = this.$store.state.organisation
        if (vm.routeName === 'EmployeeDetail') {
          Search.employees(org.uuid, query)
            .then(response => {
              vm.items = response.length > 0 ? response : vm.noItem
            })
        }

        if (vm.routeName === 'OrganisationDetail') {
          Search.organisations(org.uuid, query)
            .then(response => {
              vm.items = response
            })
        }
      },

      selected (item) {
        if (item.uuid == null) return
        this.items = []
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