import { Service } from './HttpCommon'
import { EventBus } from '@/EventBus'
import store from '@/vuex/store'

export default {

  /**
   * Get a list of all employees
   * @returns {Array} List of all employees
   */
  getAll (orgUuid) {
    return Service.get(`/o/${orgUuid}/e/`)
      .then(response => {
        return response.data.items
      })
      .catch(error => {
        console.log(error.response)
      })
  },

  /**
   * Get an employee
   * @param {String} uuid - uuid for employee
   * @returns {Object} employee object
   */
  get (uuid) {
    return Service.get(`/e/${uuid}/`)
      .then(response => {
        EventBus.$emit('organisation-changed', response.data.org)
        return response.data
      })
      .catch(error => {
        store.commit('log/newError', {type: 'ERROR', value: error.response})
      })
  },

  history (uuid) {
    return Service.get(`/e/${uuid}/history/`)
      .then(response => {
        return response.data
      })
  },

  /**
   * Get engagement details for employee
   * @param {String} uuid - employee uuid
   * @see getDetail
   */
  getEngagementDetails (uuid, validity) {
    return this.getDetail(uuid, 'engagement', validity)
  },

  /**
   * Base call for getting details.
   * @param {String} uuid - employee uuid
   * @param {String} detail - Name of the detail
   * @returns {Array} A list of options for the detail
   */
  getDetail (uuid, detail, validity) {
    validity = validity || 'present'
    return Service.get(`/e/${uuid}/details/${detail}?validity=${validity}`)
      .then(response => {
        return response.data
      })
      .catch(error => {
        store.commit('log/newError', {type: 'ERROR', value: error.response})
      })
  },

  new (employee) {
    return Service.post(`/e/create`, employee)
      .then(response => {
        store.commit('log/newWorkLog', {type: 'EMPLOYEE_CREATE', value: response.data})
        return response.data
      })
      .catch(error => {
        store.commit('log/newError', {type: 'ERROR', value: error.response})
      })
  },

  /**
   * Create a new employee
   * @param {String} uuid - employee uuid
   * @param {Array} create - A list of elements to create
   * @returns {Object} employee uuid
   */
  createEntry (uuid, create) {
    return Service.post(`/e/${uuid}/create`, create)
      .then(response => {
        EventBus.$emit('employee-changed')
        return response.data
      })
      .catch(error => {
        store.commit('log/newError', {type: 'ERROR', value: error.response})
        EventBus.$emit('employee-changed')
      })
  },

  create (uuid, create) {
    return this.createEntry(uuid, create)
      .then(response => {
        store.commit('log/newWorkLog', {type: 'EMPLOYEE_CREATE', value: response})
      })
  },

  leave (uuid, leave) {
    return this.createEntry(uuid, leave)
      .then(response => {
        store.commit('log/newWorkLog', {type: 'EMPLOYEE_LEAVE', value: response})
      })
  },

  /**
   * Edit an employee
   * @param {String} uuid - employee uuid
   * @param {Array} edit - A list of elements to edit
   * @returns {Object} employeee uuid
   */
  edit (uuid, edit) {
    return Service.post(`/e/${uuid}/edit`, edit)
      .then(response => {
        EventBus.$emit('employee-changed')
        store.commit('log/newWorkLog', {type: 'EMPLOYEE_EDIT', value: response.data})
        return response.data
      })
      .catch(error => {
        store.commit('log/newError', {type: 'ERROR', value: error.response})
      })
  },

  move (uuid, move) {
    return this.edit(uuid, move)
      .then(response => {
        store.commit('log/newWorkLog', {type: 'EMPLOYEE_MOVE', value: response})
      })
  },

  /**
   * End an employee
   * @param {String} uuid - employee uuid
   * @param {Object} end - Object containing the end date
   * @returns {Object} employee uuid
   */
  terminate (uuid, end) {
    return Service.post(`/e/${uuid}/terminate`, end)
      .then(response => {
        EventBus.$emit('employee-changed')
        store.commit('log/newWorkLog', {type: 'EMPLOYEE_TERMINATE', value: response.data})
        return response.data
      })
      .catch(error => {
        store.commit('log/newError', {type: 'ERROR', value: error.response})
      })
  }
}
