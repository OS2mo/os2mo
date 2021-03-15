SPDX-FileCopyrightText: 2018-2020 Magenta ApS
SPDX-License-Identifier: MPL-2.0
<template>
  <div>
    <b-tabs v-model="tabIndex" lazy>
      <b-tab @click="navigateToTab('#engagement')" href="#engagement" :title="$t('tabs.engagement.engagement')">
        <mo-table-detail
          type="ENGAGEMENT"
          :uuid="uuid"
          :content="content['engagement']"
          content-type="engagement"
          :columns="engagement"
          @show="loadContent('engagement', $event)"
          :entry-component="!hideActions ? components.engagement : undefined"
          hide-create
        />
      </b-tab>
    </b-tabs>
  </div>
</template>

<script>
/**
 * A engagement detail tabs component.
 */

import { mapGetters } from 'vuex'
import { MoEngagementEntry, MoEmployeeAddressEntry, MoItSystemEntry, MoAssociationEntry } from '@/components/MoEntry'
import MoTableDetail from '@/components/MoTable/MoTableDetail'
import bTabs from 'bootstrap-vue/es/components/tabs/tabs'
import bTab from 'bootstrap-vue/es/components/tabs/tab'
import { Facet } from '@/store/actions/facet'
import { AtDate } from '@/store/actions/atDate'

export default {
  components: {
    MoTableDetail,
    'b-tabs': bTabs,
    'b-tab': bTab
  },

  props: {
    /**
     * Defines a unique identifier which must be unique.
     */
    uuid: String,

    content: Object,

    /**
     * This Boolean property hides the actions.
     */
    hideActions: Boolean
  },

  data () {
    return {
      tabIndex: 0,
      tabs: ['#engagement', '#adresser', '#it', '#tilknytninger'],
      currentDetail: 'engagement',
      _atDate: undefined,
      /**
       * The leave, it, address, engagement, association, role, manager component value.
       * Used to detect changes and restore the value for columns.
       */
      role: [
        { label: 'org_unit', data: 'org_unit' },
        { label: 'role_type', data: 'role_type' }
      ],
      it: [
        { label: 'it_system', data: 'itsystem' },
        { label: 'user_key', data: null, field: 'user_key' }
      ],
      leave: [
        { label: 'leave_type', data: 'leave_type' },
        { label: 'engagement', field: null, data: 'engagement' }
      ],
      manager: [
        { label: 'org_unit', data: 'org_unit' },
        { label: 'responsibility', data: 'responsibility' },
        { label: 'manager_type', data: 'manager_type' },
        { label: 'manager_level', data: 'manager_level' }
      ],
      address: [
        { label: 'address_type', data: 'address_type' },
        { label: 'visibility', data: 'visibility' },
        { label: 'address', data: null }
      ],

      /**
       * Used to add the components in the tabs.
       */
      components: {
        engagement: MoEngagementEntry,
        address: MoEmployeeAddressEntry,
        it: MoItSystemEntry,
        association: MoAssociationEntry,
      }
    }
  },

  computed: {
    engagement () {
      let conf = this.$store.getters['conf/GET_CONF_DB']

      let columns = [
        { label: 'org_unit', data: 'org_unit' },
        { label: 'job_function', data: 'job_function' },
        { label: 'engagement_type', data: 'engagement_type' }
      ]

      if (conf.show_primary_engagement) {
        columns.splice(2, 0,
          { label: 'primary', data: 'primary' }
        )
      }

      return columns
    },

    association () {
      let conf = this.$store.getters['conf/GET_CONF_DB']
      let facet_getter = this.$store.getters[Facet.getters.GET_FACET]
      let columns = [
        { label: 'org_unit', data: 'org_unit' },
        { label: 'first_party_association_type', data: 'first_party_association_type' },
        { label: 'third_party_associated', data: 'third_party_associated' },
        { label: 'third_party_association_type', data: 'third_party_association_type' }
      ]

      if (conf.association_dynamic_facets) {
        let dynamics = conf.association_dynamic_facets.split(',').filter(elem => elem != "")
        // Function called to determine header label
        let label_function_generator = function(uuid) {
            return function() {
                return facet_getter(uuid)['description']
            }
        }
        for (const dynamic of dynamics) {
          this.$store.dispatch(Facet.actions.SET_FACET, {facet: dynamic, full: true})
          columns.push({
            label: 'dynamic_class', label_function: label_function_generator(dynamic), data: dynamic
          })
        }
      }

      if (conf.show_primary_association) {
        columns.splice(1, 0,
          { label: 'primary', data: 'primary' }
        )
      }

      return columns
    },

    ...mapGetters({
      atDate: AtDate.getters.GET,
    }),
  },

  watch: {
    atDate (newVal) {
      this._atDate = newVal
      for (var validity of ['present', 'past', 'future']) {
        this.loadContent(this.currentDetail, validity)
      }
    },
  },

  created () {
    this._atDate = this.$store.getters[AtDate.getters.GET]
  },

  mounted () {
    this.tabIndex = this.tabs.findIndex(tab => tab == this.$route.hash)
  },

  methods: {
    loadContent (contentType, event) {
      let payload = {
        uuid: this.uuid,
        detail: contentType,
        validity: event,
        atDate: this._atDate,
        extra: contentType === 'association' ? {'first_party_perspective': '1'} : {},
      }
      this.currentDetail = contentType
      this.$emit('show', payload)
    },

    navigateToTab (tabTarget) {
      this.$router.replace(tabTarget)
    }
  }
}
</script>
