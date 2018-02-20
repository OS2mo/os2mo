import { HTTP, Service } from './HttpCommon'
import { EventBus } from '../EventBus'

export default {

  /**
   * Get an organisation unit
   * @param {String} uuid - organisation unit uuid
   * @returns {Object} organisation unit object
   */
  get (uuid) {
    return Service.get(`/ou/${uuid}`)
    .then(response => {
      return response.data
    })
    .catch(e => {
      console.log(e)
    })
  },

  /**
   * Get an tree unit
   * @param {String} uuid - tree unit uuid
   * @returns {Object} tree unit object
   */
  getTree (uuid) {
    return Service.get(`/ou/${uuid}/tree`)
    .then(response => {
      return response.data
    })
    .catch(e => {
      console.log(e)
    })
  },

  /**
   * Get an organisation unit
   * @param {String} uuid - organisation unit uuid
   * @returns {Array} organisation unit children
   */
  getChildren (uuid, atDate) {
    atDate = atDate || new Date()
    return Service.get(`/ou/${uuid}/children?at=${atDate.toISOString()}`)
    .then(response => {
      return response.data
    })
    .catch(e => {
      console.log(e)
    })
  },

  /**
   * Get the history of all changes made to an organisation unit
   * @param {String} uuid - Uuid for the current organisation unit
   * @returns {Array} A list of historical events for the organisation unit
   */
  getHistory (uuid) {
    return HTTP.get(`/org-unit/${uuid}/history/`)
    .then(response => {
      return response.data
    })
  },

   /**
   * Get organisation unit details
   * @see getDetail
   */
  getUnitDetails (uuid, validity) {
    return this.getDetail(uuid, 'unit', validity)
  },

  /**
   * Get location details
   * @see getDetail
   */
  getLocationDetails (uuid, validity) {
    return this.getDetail(uuid, 'location', validity)
  },

  /**
   * Get contact channel details
   * @see getDetail
   */
  getContactDetails (uuid, validity) {
    return this.getDetail(uuid, 'contact-channel', validity)
  },

  /**
   * Get engagement details
   * @see getDetail
   */
  getEngagementDetails (uuid, validity) {
    return this.getDetailNew(uuid, 'engagement')
  },

  /**
   * Base call for getting details.
   * @param {String} uuid - organisation unit uuid
   * @param {String} detail - Name of the detail
   * @returns {Array} A list of options for the detail
   */
  getDetailNew (uuid, detail) {
    return Service.get(`/ou/${uuid}/details/${detail}`)
    .then(response => {
      return response.data
    })
  },

  getDetailList (uuid) {
    return Service.get(`/ou/${uuid}/details`)
    .then(response => {
      return response.data
    })
  },

  /**
   * Base call for getting details.
   * @todo Need a fix to the api so the current handling of detail is not needed
   * @todo validity could maybe get a better name
   * @todo maybe create an enum for validity
   * @param {String} uuid - Uuid for the current organisation unit
   * @param {String} detail - Name of the detail to get
   * @param {String} validity - Can be 'past', 'present' or 'future'
   * @returns {Array} A list of options for the specififed detail
   * @deprecated
   */
  getDetail (uuid, detail, validity) {
    detail = detail === 'unit' ? '' : '/role-types/' + detail
    validity = validity || 'present'
    return HTTP.get(`/org-unit/${uuid}${detail}/?validity=${validity}`)
    .then(response => {
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  },

    /**
   * Create a new organisation unit
   * @param {Object} orgUnit - new organisation unit
   * @returns {Object} organisation unit uuid
   */
  create (orgUnit) {
    return HTTP.post('/org-unit', orgUnit)
    .then(response => {
      EventBus.$emit('org-unit-create', response.data)
      return response.data
    })
  },

    /**
   * Rename an organisation unit
   * @param {Object} orgUnit - organisation unit to rename
   * @param {String} newName - new name of the organisation unit
   * @returns {Object} organisation unit uuid
   */
  rename (orgUnit, newName) {
    orgUnit.name = newName
    return HTTP.post(`/org-unit/${orgUnit.uuid}?rename=true`, orgUnit)
    .then(response => {
      EventBus.$emit('org-unit-rename', response.data)
      return response.data
    })
  },

  /**
   * Edit an organisation unit
   * @param {String} uuid - organisation unit uuid
   * @param {Array} edit - A list of elements to edit
   * @returns {Object} organisation unit uuid
   */
  edit (uuid, edit) {
    return Service.post(`/ou/${uuid}/edit`, edit)
    .then(response => {
      EventBus.$emit('organisation-unit-changed', response.data)
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  },

  /**
   * Terminate a organisation unit
   * @param {Object} uuid - the organisation unit to end
   * @param {String} terminate - the date on which the organisation unit shall end
   * @returns {Object} organisation unit uuid
   */
  terminate (uuid, terminate) {
    return Service.post(`/ou/${uuid}/terminate`, terminate)
    .then(response => {
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  }
}
