import { Service } from './HttpCommon'
import { EventBus } from '../EventBus'

export default {

  /**
   * Get an organisation unit
   * @param {String} uuid - organisation unit uuid
   * @returns {Object} organisation unit object
   */
  get (uuid) {
    return Service.get(`/ou/${uuid}/`)
      .then(response => {
        EventBus.$emit('organisation-changed', response.data.org)
        return response.data
      })
      .catch(error => {
        EventBus.$emit('mo-error', error.response)
      })
  },

  /**
   * Get an organisation unit
   * @param {String} uuid - organisation unit uuid
   * @returns {Array} organisation unit children
   */
  getChildren (uuid, atDate) {
    atDate = atDate || new Date()
    if (atDate instanceof Date) atDate = atDate.toISOString().split('T')[0]
    return Service.get(`/ou/${uuid}/children?at=${atDate}`)
      .then(response => {
        return response.data
      })
      .catch(error => {
        EventBus.$emit('mo-error', error.response)
      })
  },

  /**
   * Get the history of all changes made to an organisation unit
   * @param {String} uuid - Uuid for the current organisation unit
   * @returns {Array} A list of historical events for the organisation unit
   */
  history (uuid) {
    return Service.get(`/ou/${uuid}/history/`)
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
   * Get address for organisation unit details
   * @see getDetail
   */
  getAddressDetails (uuid, validity) {
    return this.getDetail(uuid, 'address', validity)
  },

  /**
   * Base call for getting details.
   * @param {String} uuid - organisation unit uuid
   * @param {String} detail - Name of the detail
   * @param {String} validity - Can be either past, present or future
   * @returns {Array} A list of options for the detail
   */
  getDetail (uuid, detail, validity, atDate) {
    validity = validity || 'present'
    atDate = atDate || new Date()
    if (atDate instanceof Date) atDate = atDate.toISOString().split('T')[0]
    return Service.get(`/ou/${uuid}/details/${detail}?validity=${validity}&at=${atDate}`)
      .then(response => {
        return response.data
      })
      .catch(error => {
        EventBus.$emit('mo-error', error.response)
      })
  },

  /**
   * Create a new organisation unit
   * @param {Object} orgUnit - new organisation unit
   * @param {Array} create - A list of elements to edit
   * @returns {Object} organisation unit uuid
   */
  create (create) {
    return Service.post('/ou/create', create)
      .then(response => {
        EventBus.$emit('organisation-unit-changed')
        EventBus.$emit('organisation-unit-create', response.data)
        return response.data
      })
      .catch(error => {
        EventBus.$emit('mo-error', error.response)
      })
  },

  /**
   * Create a new organisation unit entry
   * @param {Object} orgUnit - new organisation unit
   * @param {String} uuid - organisation uuid
   * @param {Array} create - A list of elements to edit
   * @returns {Object} organisation unit uuid
   */
  createEntry (uuid, create) {
    return Service.post(`/ou/${uuid}/create`, create)
      .then(response => {
        EventBus.$emit('organisation-unit-changed', response.data)
        EventBus.$emit('organisation-unit-create', response.data)
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
  editEntry (uuid, edit) {
    return Service.post(`/ou/${uuid}/edit`, edit)
      .then(response => {
        EventBus.$emit('organisation-unit-changed')
        return response.data
      })
      .catch(error => {
        EventBus.$emit('mo-error', error.response)
        EventBus.$emit('organisation-unit-changed')
      })
  },

  edit (uuid, edit) {
    return this.editEntry(uuid, edit)
      .then(response => {
        EventBus.$emit('organisation-unit-edit', response)
        return response
      })
  },

  /**
   * Rename a new organisation unit
   * @param {String} uuid - organisation unit uuid
   * @param {Array} edit - A list of elements to edit
   * @returns {Object} organisation unit uuid
   * @see edit
  */
  rename (uuid, edit) {
    return this.editEntry(uuid, edit)
      .then(response => {
        EventBus.$emit('organisation-unit-rename', response)
        return response
      })
  },

  /**
   * Move a new organisation unit
   * @param {String} uuid - organisation unit uuid
   * @param {Array} edit - A list of elements to edit
   * @returns {Object} organisation unit uuid
   * @see edit
  */
  move (uuid, edit) {
    return this.editEntry(uuid, edit)
      .then(response => {
        EventBus.$emit('organisation-unit-move', response)
        return response
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
        EventBus.$emit('organisation-unit-changed')
        EventBus.$emit('organisation-unit-terminate', response.data)
        return response.data
      })
      .catch(error => {
        EventBus.$emit('mo-error', error.response)
      })
  }
}
