import { Service } from './HttpCommon'
import { EventBus } from '../EventBus'

let selectedOrganisation = {}

export default {

  /**
   * Get a list of all organisations
   * @returns {Array} List of all organisations
   */
  getAll (atDate) {
    atDate = atDate || ''
    return Service.get(`/o/?at=${atDate}`)
      .then(response => {
        return response.data
      })
  },

  /**
   * Get an organisation
   * @param {String} OrgUuid - Uuid for the organisation to get
   * @returns {Object} an organisation object
   */
  get (uuid) {
    Service.get('/o/' + uuid)
      .then(response => {
        return response.data
      })
  },

    /**
   * Get the children of an organisation
   * @param {String} uuid - Uuid for current organisation
   * @returns {Array} List of organisation units within the organisation
   */
  getChildren (uuid) {
    return Service.get(`/o/${uuid}/children`)
      .then(response => {
        return response.data
      })
  },

  /**
   * Set the selected organisation
   * @param {Object} org - the organisation to set
   */
  setSelectedOrganisation (org) {
    selectedOrganisation = org
    EventBus.$emit('organisation-changed', selectedOrganisation)
  },

  /**
   * Get the selected organisation
   * @returns {Object} an organisation object
   */
  getSelectedOrganisation () {
    return selectedOrganisation
  }

  /** **************************************************** */
  /** REFACTOR FROM HERE, THIS SHOULD BE ORGANISATION UNIT */
  /** **************************************************** */

  /**
   * Get an orgaisation unit
   * @param {String} unitUuid - Uuid for the organisation unit
   * @returns {Object} an organisation unit object
   */
  // getOrganisationUnit (unitUuid) {
  //   let vm = this
  //   return HTTP.get(`/org-unit/${unitUuid}`)
  //   .then(response => {
  //     selectedOrgUnit = response.data[0]
  //     EventBus.$emit('organisation-unit-changed', selectedOrgUnit)

  //     if (selectedOrganisation === '') {
  //       vm.getOrganisation(selectedOrgUnit.org)
  //     }

  //     return response.data[0]
  //   })
  // },
}
