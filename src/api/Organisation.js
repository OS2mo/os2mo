import { Service } from './HttpCommon'
import { EventBus } from '../EventBus'

let selectedOrganisation = {}

export default {

  /**
   * Get a list of all organisations
   * @param {Date} atDate - the date
   * @returns {Array} List of all organisations
   */
  getAll (atDate) {
    atDate = atDate || new Date()

    return Service.get(`/o/?at=${atDate.toISOString()}`)
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
    return Service.get(`/o/${uuid}/`)
      .then(response => {
        return response.data
      })
  },

    /**
   * Get the children of an organisation
   * @param {String} uuid - Uuid for current organisation
   * @param {Date} atDate - Date
   * @returns {Array} List of organisation units within the organisation
   */
  getChildren (uuid, atDate) {
    atDate = atDate || new Date()
    return Service.get(`/o/${uuid}/children?at=${atDate.toISOString()}`)
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
}
