<template>
    <div class="input-group">
      <span class="input-group-addon">
        <icon name="search"/>
      </span>
      <v-autocomplete 
        :items="results"
        name="search"
        :get-label="getLabel" 
        :component-item="template" 
        @update-items="getSearchResults"
        @untouched="results=[]"
        item-selected="updateResult"
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
        selected: {},
        template: TheSearchBarTemplate
      }
    },
    created () {},
    watch: {
      selected (newVal) {
        console.log(newVal)
        this.$router.push({ name: 'EmployeeDetail', params: { userId: newVal.uuid }})
        // this.$router.push({
        //   name: 'EmployeeDetail',
        //   params: {
        //     uuid: newVal.uuid
        //   }
        // })
      }
    },
    methods: {
      getLabel (item) {
        this.selected = item
        return item.name
      },

      getSearchResults (query) {
        let vm = this
        let org = Organisation.getSelectedOrganisation()
        Search.employees(org.uuid, query)
        .then(response => {
          vm.results = response
        })
      },

      updateResult () {
        console.log('upate result')
        console.log(this.selected)
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  .input-group {
    width: 500px;
  }

  .v-autocomplete {
    .v-autocomplete-input-group {
      .v-autocomplete-input {
        display: block;
        width: 100%;
        padding: 0.375rem 0.75rem;
        font-size: 1rem;
        line-height: 1.5;
        color: #495057;
        background-color: #fff;
        background-image: none;
        background-clip: padding-box;
        border: 1px solid #ced4da;
        border-radius: 0.25rem;
        transition: border-color ease-in-out 0.15s, box-shadow ease-in-out 0.15s;
      }
    }
    .v-autocomplete-list {
      z-index: 999;
      background-color: #fff;
      width: 100%;
      padding: 0.375rem 0.75rem;
      border: 1px solid #ced4da;
      border-radius: 0 0 0.25rem;
      transition: border-color ease-in-out 0.15s, box-shadow ease-in-out 0.15s;
    }
  }
</style>