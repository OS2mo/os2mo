SPDX-FileCopyrightText: 2017-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0

<script>
/**
 * A organisation unit picker component.
 */

import { mapGetters } from 'vuex'
import MoTreePicker from '@/components/MoPicker/MoTreePicker'
import Organisation from '@/api/Organisation'
import OrganisationUnit from '@/api/OrganisationUnit'
import Search from '@/api/Search'
import { Organisation as OrgStore } from '@/store/actions/organisation'
import { AtDate } from '@/store/actions/atDate'

export default {
  name: 'MoOrganisationUnitPicker',

  extends: MoTreePicker,

  data () {
    return {
      fetchSearchResultsTimeout: null,
      _atDate: undefined,
    }
  },

  computed: {
    ...mapGetters({
      atDate: AtDate.getters.GET,
    }),
  },

  created () {
    this._atDate = this.$store.getters[AtDate.getters.GET]
  },

  watch: {
    // Respond to changes in the 'atDate' global state.
    atDate (newVal) {
      this._atDate = newVal
    },

    // Whenever 'unitName' changes, update the matching search results in
    // autocomplete dropdown. ('unitName' is bound to the text input field in
    // `MoTreePicker`.)
    unitName: {
      deep: true,
      async handler (newVal, oldVal) {
        // Don't fetch search results if the tree picker is already bound to a
        // value, and that value is equal to the text in the input field.
        if ((this.value != null) && (this.value.name === newVal)) {
          return
        }

        // User just clicked a search result, so don't re-display a new set of
        // search results.
        if (this.searchResultSelected) {
          this.searchResultSelected = false
          return
        }

        // A request for search results is currently in-flight, so do nothing.
        if (this.searchResultLoading) {
          return
        }

        if (newVal && newVal.length > 1) {
          if (this.fetchSearchResultsTimeout) {
            clearTimeout(this.fetchSearchResultsTimeout)
          }
          this.fetchSearchResultsTimeout = setTimeout(
            () => { this.fetchSearchResults(newVal) },
            500,
          )
        } else {
          this.updateSearchResults(newVal, [])
        }
      }
    }
  },

  methods: {
    get_name_id() {
      return 'org-unit-' + this._uid
    },

    get_validations() {
      return {
        orgunit: [this.validity, this.unitUuid]
      }
    },

    async get_entry(uuid) {
      return await OrganisationUnit.get(uuid, this._atDate)
    },

    get_ancestor_tree(uuid, date) {
      return OrganisationUnit.getAncestorTree(uuid, date)
    },

    get_toplevel_children(uuid, date) {
      return Organisation.getChildren(uuid, date)
    },

    get_children(uuid, date) {
      return OrganisationUnit.getChildren(uuid, date)
    },

    get_store_uuid() {
      /**
       * The tree view itself is dependent on the currently active
       * organisation. Among other things, we should only show the units
       * for that organisation, and also ensure that we reset the view
       * whenever it changes.
       */
      return OrgStore.getters.GET_UUID
    },

    fetchSearchResults(query) {
      this.searchResultLoading = true

      let org = this.$store.state.organisation
      let date = this._atDate
      let details = "path"

      Search.organisations(org.uuid, query, date, details).then(
        response => {this.updateSearchResults(query, response)}
      )
    },

    updateSearchResults(query, response) {
      if (response && response.length) {
        // Add 'path' property to each item in response
        // Each path is an array where each element is part of the org unit
        // path.
        for (var result of response) {
          let parts = result.location.split('\\')
          if ((parts.length > 0) && (parts[0] !== '')) {
            result.path = parts
            result.path.push(result['name'])
          } else {
            result.path = [result['name']]
          }
        }

        // Sort search results based on how many times each result match the
        // search query.
        let numOccurrences = function(result) {
          let path = `${result.location}\\${result.name}`
          let pattern = new RegExp(query, "gi")
          return (path.match(pattern) || []).length
        }
        let sortedResults = response.sort((a, b) => {
          return numOccurrences(a) - numOccurrences(b)
        })

        // Update search results on screen
        this.showTree = false
        this.searchResultLoading = false
        this.searchResults = sortedResults
      }

      if ((response === null) || (response.length === 0)) {
        this.showTree = false
        this.searchResultLoading = false
        this.searchResults = []
      }
    },

    selectSearchResult(result) {
      this.showTree = false
      this.searchResultLoading = false
      this.searchResults = []
      this.searchResultSelected = true
      this.selectedSuperUnitUuid = result['uuid']
    },
  }
}
</script>
