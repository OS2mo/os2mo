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
  history (uuid) {
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
    return this.getDetail(uuid, 'engagement', validity)
  },

  /**
   * Base call for getting details.
   * @param {String} uuid - organisation unit uuid
   * @param {String} detail - Name of the detail
   * @param {String} validity - Can be either past, present or future
   * @returns {Array} A list of options for the detail
   */
  getDetail (uuid, detail, validity) {
    validity = validity || 'present'
    return Service.get(`/ou/${uuid}/details/${detail}?validity=${validity}`)
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
   * Create a new organisation unit
   * @param {Object} orgUnit - new organisation unit
   * @param {Array} edit - A list of elements to edit
   * @returns {Object} organisation unit uuid
   */
  create (create) {
    return Service.post('/ou/create', create)
    .then(response => {
      EventBus.$emit('organisation-unit-created', response.data)
      return response.data
    })
    .catch(error => {
      console.log(error.response)
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
