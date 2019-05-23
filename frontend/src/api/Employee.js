import Service from './HttpCommon'
import { EventBus, Events } from '@/EventBus'
import store from '@/store'

export default {

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
        store.commit('log/newError', { type: 'ERROR', value: error.response })
      })
  },

  new (employee) {
    return Service.post('/e/create', employee)
      .then(response => {
        let employeeUuid = response.data
        if (Array.isArray(response.data)) {
          employeeUuid = response.data[0]
        }
        if (response.data.error) {
          return response.data
        }
        store.commit('log/newWorkLog', { type: 'EMPLOYEE_CREATE', value: employeeUuid })
        return employeeUuid
      })
      .catch(error => {
        store.commit('log/newError', { type: 'ERROR', value: error.response.data })
        return error.response.data
      })
  },

  /**
   * Create a new employee
   * @param {String} uuid - employee uuid
   * @param {Array} create - A list of elements to create
   * @returns {Object} employee uuid
   */
  createEntry (create) {
    return Service.post('/details/create', create)
      .then(response => {
        EventBus.$emit(Events.EMPLOYEE_CHANGED)
        return response
      })
      .catch(error => {
        EventBus.$emit(Events.EMPLOYEE_CHANGED)
        store.commit('log/newError', { type: 'ERROR', value: error.response })
        return error.response
      })
  },

  create (create) {
    return this.createEntry(create)
      .then(response => {
        if (response.data.error) {
          return response.data
        }
        return response.data
      })
  },

  /**
   * Edit an employee
   * @param {String} uuid - employee uuid
   * @param {Array} edit - A list of elements to edit
   * @returns {Object} employeee uuid
   */
  edit (edit) {
    return Service.post('/details/edit', edit)
      .then(response => {
        EventBus.$emit(Events.EMPLOYEE_CHANGED)
        return response.data
      })
      .catch(error => {
        store.commit('log/newError', { type: 'ERROR', value: error.response.data })
        return error.response.data
      })
  }
}
