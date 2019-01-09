import Service from './HttpCommon'
import { EventBus } from '@/EventBus'
import store from '@/store'
import URLSearchParams from '@ungap/url-search-params'

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
        store.commit('log/newError', { type: 'ERROR', value: error.response })
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
        store.commit('log/newError', { type: 'ERROR', value: error.response })
      })
  },

  /**
   * Get an organisation unit
   * @param {Array|String} uuids - organisation unit uuid
   * @returns {Array} organisation unit children
   */
  getAncestorTree (uuids, atDate) {
    atDate = atDate || new Date()
    if (atDate instanceof Date) atDate = atDate.toISOString().split('T')[0]

    if (!(uuids instanceof Array)) {
      uuids = [uuids]
    }

    const params = new URLSearchParams()

    if (atDate) {
      params.append('at', atDate)
    }

    for (const uuid of uuids) {
      params.append('uuid', uuid)
    }

    return Service.get('/ou/ancestor-tree?' + params.toString())
      .then(response => {
        return response.data[0]
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
      .then(response => {
        response.forEach(addr => {
          delete addr.validity
        })
        return response
      })
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
        store.commit('log/newError', { type: 'ERROR', value: error.response })
      })
  },

  /**
   * Create a new organisation unit
   * @param {Object} orgUnit - new organisation unit
   * @param {Array} create - A list of elements to create
   * @returns {Object} organisation unit uuid
   */
  create (create) {
    return Service.post('/ou/create', create)
      .then(response => {
        EventBus.$emit('update-tree-view')
        store.commit('log/newWorkLog', { type: 'ORGANISATION_CREATE', value: response.data })
        return response.data
      })
      .catch(error => {
        store.commit('log/newError', { type: 'ERROR', value: error.response.data })
        return error.response.data
      })
  },

  /**
   * Create a new organisation unit entry
   * @param {Object} orgUnit - new organisation unit
   * @param {String} uuid - organisation uuid
   * @param {Array} create - A list of elements to create
   * @returns {Object} organisation unit uuid
   */
  createEntry (create) {
    return Service.post('/details/create', create)
      .then(response => {
        EventBus.$emit('organisation-unit-changed')
        store.commit('log/newWorkLog', { type: 'ORGANISATION_CREATE', value: response.data })
        return response.data
      })
      .catch(error => {
        store.commit('log/newError', { type: 'ERROR', value: error.response })
        return error.response
      })
  },

  /**
   * Edit an organisation unit
   * @param {String} uuid - organisation unit uuid
   * @param {Array} edit - A list of elements to edit
   * @returns {Object} organisation unit uuid
   */
  editEntry (edit) {
    return Service.post('/details/edit', edit)
      .then(response => {
        EventBus.$emit('update-tree-view')
        EventBus.$emit('organisation-unit-changed')
        return response
      })
      .catch(error => {
        store.commit('log/newError', { type: 'ERROR', value: error.response })
        return error.response
      })
  },

  edit (edit) {
    return this.editEntry(edit)
      .then(response => {
        store.commit('log/newWorkLog', { type: 'ORGANISATION_EDIT', value: response.data })
        return response.data
      })
  },

  /**
   * Rename a new organisation unit
   * @param {String} uuid - organisation unit uuid
   * @param {Array} edit - A list of elements to edit
   * @returns {Object} organisation unit uuid
   * @see edit
  */
  rename (edit) {
    return this.editEntry(edit)
      .then(response => {
        store.commit('log/newWorkLog', { type: 'ORGANISATION_RENAME', value: response.data })
        return response.data
      })
  },

  /**
   * Move a new organisation unit
   * @param {String} uuid - organisation unit uuid
   * @param {Array} edit - A list of elements to edit
   * @returns {Object} organisation unit uuid
   * @see edit
  */
  move (edit) {
    return this.editEntry(edit)
      .then(response => {
        if (response.data.error) {
          return response.data
        }
        EventBus.$emit('update-tree-view')
        store.commit('log/newWorkLog', { type: 'ORGANISATION_MOVE', value: response.data })
        return response.data
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
        EventBus.$emit('update-tree-view')
        EventBus.$emit('organisation-unit-changed')
        store.commit('log/newWorkLog', { type: 'ORGANISATION_TERMINATE', value: response.data })
        return response.data
      })
      .catch(error => {
        store.commit('log/newError', { type: 'ERROR', value: error.response.data })
        return error.response.data
      })
  }
}
