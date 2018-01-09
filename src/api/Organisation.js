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
    return HTTP.get('/o/')
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
   * Get an organisation
   * @param {String} OrgUuid - Uuid for the organisation to get
   * @returns {Object} an organisation object
   */
  getOrganisation (orgUuid) {
    let vm = this
    HTTP.get('/o/' + orgUuid)
      .then(response => {
        vm.setSelectedOrganisation(response.data)
      })
  },

  /**
   * Get an orgaisation unit
   * @param {String} unitUuid - Uuid for the organisation unit
   * @returns {Object} an organisation unit object
   */
  getOrganisationUnit (unitUuid) {
    let orgUuid = '00000000-0000-0000-0000-000000000000'
    let vm = this
    return HTTP.get('/o/' + orgUuid + '/org-unit/?query=' + unitUuid)
    .then(function (response) {
      selectedOrgUnit = response.data[0]
      EventBus.$emit('organisation-unit-changed', selectedOrgUnit)

      if (selectedOrganisation === '') {
        vm.getOrganisation(selectedOrgUnit.org)
      }

      return response.data[0]
    })
  },

  /**
   * Get the selected organisation
   * @returns {Object} an organisation object
   */
  getSelectedOrganisation () {
    return selectedOrganisation
  },

  /**
   * Get the selected organisation unit
   * @returns {Object} an organisation unit object
   */
  getSelectedOrganisationUnit () {
    return selectedOrgUnit
  },

  /**
   * Get the hierachy of an organisation
   * @param {String} orgUuid - Uuid for current organisation
   * @returns {Array} List of organisation units within the organisation
   */
  getFullHierachy (orgUuid, unitUuid) {
    unitUuid = unitUuid || ''
    let append = unitUuid ? '?treeType=specific&orgUnitId=' + unitUuid : ''
    return HTTP.get('/o/' + orgUuid + '/full-hierarchy' + append)
      .then(response => {
        return response.data
      })
  },

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
   * Get leader details
   * @see getDetail
   */
  getLeaderDetails (unitUuid, validity) {
    return this.getDetail(unitUuid, 'leader', validity)
  },

  /**
   * Get engagement details
   * @see getDetail
   */
  getEngagementDetails (unitUuid, validity) {
    return this.getDetail(unitUuid, 'engagement', validity)
  },

  /**
   * Get associaion details
   * @see getDetail
   */
  getAssociationDetails (unitUuid, validity) {
    return this.getDetail(unitUuid, 'association', validity)
  },

  /**
   * Get job function details
   * @see getDetail
   */
  getJobFunctionDetails (unitUuid, validity) {
    return this.getDetail(unitUuid, 'job-function', validity)
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
  getDetail (unitUuid, detail, validity) {
    detail = detail === 'unit' ? '' : '/role-types/' + detail
    validity = validity || 'present'
    let orgUuid = '00000000-0000-0000-0000-000000000000'
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
  getHistory (unitUuid) {
    let orgUuid = '00000000-0000-0000-0000-000000000000'
    return HTTP.get('/o/' + orgUuid + '/org-unit/' + unitUuid + '/history/')
    .then(response => {
      return response.data
    })
  },

  /**
   * Create a new organisation unit
   * @param {Object} orgUnit - new organisation unit
   * @returns {Object} organisation unit uuid
   */
  createOrganisationUnit (orgUnit) {
    return HTTP.post('/o/' + orgUnit.org + '/org-unit', orgUnit)
      .then(response => {
        return response
      })
  },

  /**
   * Rename an organisation unit
   * @param {Object} orgUnit - organisation unit to rename
   * @param {String} newName - new name of the organisation unit
   * @returns {Object} organisation unit uuid
   */
  renameOrganisationUnit (orgUnit, newName) {
    orgUnit.name = newName
    return HTTP.post('/o/' + orgUnit.org + '/org-unit/' + orgUnit.uuid + '?rename=true', orgUnit)
    .then(function (response) {
      return response.data
    })
  },

  /**
   * Move an organisation unit
   * @param {Object} orgUnit - organisation unit to move
   * @param {String} toUuid - uuid for the new parent organisation unit
   * @param {String} date - the move date
   * @returns {Object} organisation unit uuid
   */
  moveOrganisationUnit (orgUnit, toUuid, date) {
    var obj = {
      'moveDate': date,
      'newParentOrgUnitUUID': toUuid
    }

    return HTTP.post('/o/' + orgUnit.org + '/org-unit/' + orgUnit.uuid + '/actions/move', obj)
    .then(function (response) {
      return response
    })
  },

  /**
   * End an organisation
   * @param {Object} orgUnit - the organisation unit to end
   * @param {String} endDate - the date on which the organisation unit shall end
   * @returns {Object} organisation unit uuid
   */
  endOrganisationUnit (orgUnit, endDate) {
    return HTTP.delete('/o/' + orgUnit.org + '/org-unit/' + orgUnit.uuid + '?endDate=' + endDate)
    .then(response => {
      return response
    })
  }
}
