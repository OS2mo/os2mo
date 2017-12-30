import { HTTP } from './HttpCommon'
import { EventBus } from '../EventBus'

var selectedOrganisation = ''
var selectedOrgUnit = ''

export default {

  /**
   * Get a list of all organisations
   * @returns {Array} List of all organisations
   */
  getAll () {
    return HTTP.get('o/')
      .then(response => {
        return response.data
      })
  },

  getSelectedOrganisation () {
    return selectedOrganisation
  },

  setSelectedOrganisation (org) {
    selectedOrganisation = org
    EventBus.$emit('organisation-changed', selectedOrganisation)
  },

  getSelectedOrganisationUnit () {
    return selectedOrgUnit
  },

  /**
   * Get the hierachy of an organisation
   * @param {String} orgUuid - Uuid for current organisation
   * @returns {Array} List of organisation units within the organisation
   */
  getFullHierachy (orgUuid) {
    return HTTP.get('o/' + orgUuid + '/full-hierarchy')
      .then(response => {
        return response.data
      })
  },

  /**
   * Get organisation unit details
   * @see getDetail
   */
  getUnitDetails (orgUuid, unitUuid, validity) {
    return this.getDetail(orgUuid, unitUuid, 'unit', validity)
  },

  /**
   * Get location details
   * @see getDetail
   */
  getLocationDetails (orgUuid, unitUuid, validity) {
    return this.getDetail(orgUuid, unitUuid, 'location', validity)
  },

  /**
   * Get contact channel details
   * @see getDetail
   */
  getContactDetails (orgUuid, unitUuid, validity) {
    return this.getDetail(orgUuid, unitUuid, 'contact-channel', validity)
  },

  /**
   * Get leader details
   * @see getDetail
   */
  getLeaderDetails (orgUuid, unitUuid, validity) {
    return this.getDetail(orgUuid, unitUuid, 'leader', validity)
  },

  /**
   * Get engagement details
   * @see getDetail
   */
  getEngagementDetails (orgUuid, unitUuid, validity) {
    return this.getDetail(orgUuid, unitUuid, 'engagement', validity)
  },

  /**
   * Get associaion details
   * @see getDetail
   */
  getAssociationDetails (orgUuid, unitUuid, validity) {
    return this.getDetail(orgUuid, unitUuid, 'association', validity)
  },

  /**
   * Get job function details
   * @see getDetail
   */
  getJobFunctionDetails (orgUuid, unitUuid, validity) {
    return this.getDetail(orgUuid, unitUuid, 'job-function', validity)
  },

  /**
   * Base call for getting details.
   * @todo Need a fix to the api so the current handling of detail is not needed
   * @todo validity could maybe get a better name
   * @todo maybe create an enum for validity
   * @param {String} orgUuid - Uuid for the current organisation
   * @param {String} unitUuid - Uuid for the current organisation unit
   * @param {String} detail - Name of the detail to get
   * @param {String} validity - Can be 'past', 'present' or 'future'
   * @returns {Array} A list of options for the specififed detail
   */
  getDetail (orgUuid, unitUuid, detail, validity) {
    detail = detail === 'unit' ? '' : '/role-types/' + detail
    validity = validity || 'present'
    return HTTP.get('/o/' + orgUuid + '/org-unit/' + unitUuid + detail + '/?validity=' + validity)
    .then(response => {
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  },

  /**
   * Get the history of all changes made to an organisation unit
   * @param {String} orgUuid - Uuid for the current organisation
   * @param {String} unitUuid - Uuid for the current organisation unit
   * @returns {Array} A list of historical events for the organisation unit
   */
  getHistory (orgUuid, unitUuid) {
    return HTTP.get('/o/' + orgUuid + '/org-unit/' + unitUuid + '/history/')
    .then(response => {
      return response.data
    })
  },

  createOrganisationUnit (orgUnit) {
    return HTTP.post('/o/' + orgUnit.org + '/org-unit', orgUnit)
      .then(response => {
        return response
      })
  },

  renameOrganisationUnit (orgUnit) {
    return HTTP.post('/o/' + orgUnit.org + '/org-unit/' + orgUnit.uuid + '?rename=true', orgUnit)
    .then(function (response) {
      return response.data
    })
  },

  moveOrganisationUnit (orgUuid, fromUuid, toUuid, date) {
    var obj = {
      'moveDate': date,
      'newParentOrgUnitUUID': toUuid
    }

    HTTP.post('/o/' + orgUuid + '/org-unit/' + fromUuid + '/actions/move', obj)
    .then(function (response) {
      console.log('it worked!')
    })
  },

  getOrganisationUnit (orgUuid, unitUuid) {
    return HTTP.get('/o/' + orgUuid + '/org-unit/?query=' + unitUuid)
    .then(function (response) {
      selectedOrgUnit = response.data[0]
      return response.data[0]
    })
  }
}
