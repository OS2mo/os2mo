import { HTTP, Service } from './HttpCommon'
import { EventBus } from '../EventBus'

let selectedOrganisation = ''

export default {

  /**
   * Get a list of all organisations
   * @returns {Array} List of all organisations
   */
  getAll () {
    return Service.get('/o/')
      .then(response => {
        return response.data
      })
  },

  /**
   * Get an organisation
   * @param {String} OrgUuid - Uuid for the organisation to get
   * @returns {Object} an organisation object
   */
  getOrganisation (orgUuid) {
    let vm = this
    Service.get('/o/' + orgUuid)
      .then(response => {
        vm.setSelectedOrganisation(response.data)
      })
  },

    /**
   * Get the children of an organisation
   * @param {String} orgUuid - Uuid for current organisation
   * @returns {Array} List of organisation units within the organisation
   */
  getChildren (orgUuid) {
    return Service.get(`/o/${orgUuid}/children`)
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
    console.log('organisation-changed')
  },

  /**
   * Get the selected organisation
   * @returns {Object} an organisation object
   */
  getSelectedOrganisation () {
    return selectedOrganisation
  },

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

  /**
   * Get organisation unit details
   * @see getDetail
   */
  getUnitDetails (unitUuid, validity) {
    return this.getDetail(unitUuid, 'unit', validity)
  },

  /**
   * Get location details
   * @see getDetail
   */
  getLocationDetails (unitUuid, validity) {
    return this.getDetail(unitUuid, 'location', validity)
  },

  /**
   * Get contact channel details
   * @see getDetail
   */
  getContactDetails (unitUuid, validity) {
    return this.getDetail(unitUuid, 'contact-channel', validity)
  },

  /**
   * Get engagement details
   * @see getDetail
   */
  getEngagementDetails (unitUuid, validity) {
    return this.getDetail(unitUuid, 'engagement', validity)
  },

  /**
   * Base call for getting details.
   * @todo Need a fix to the api so the current handling of detail is not needed
   * @todo validity could maybe get a better name
   * @todo maybe create an enum for validity
   * @param {String} unitUuid - Uuid for the current organisation unit
   * @param {String} detail - Name of the detail to get
   * @param {String} validity - Can be 'past', 'present' or 'future'
   * @returns {Array} A list of options for the specififed detail
   */
  getDetail (unitUuid, detail, validity) {
    detail = detail === 'unit' ? '' : '/role-types/' + detail
    validity = validity || 'present'
    return HTTP.get(`/org-unit/${unitUuid}${detail}/?validity=${validity}`)
    .then(response => {
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  },

  /**
   * Get the history of all changes made to an organisation unit
   * @param {String} unitUuid - Uuid for the current organisation unit
   * @returns {Array} A list of historical events for the organisation unit
   */
  getHistory (unitUuid) {
    return HTTP.get(`/org-unit/${unitUuid}/history/`)
    .then(response => {
      return response.data
    })
  }
}
