import Service from './HttpCommon'
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
    return Service.post('/e/create', employee)
      .then(response => {
        let EmployeeUuid = response.data
        if (Array.isArray(response.data)) {
          EmployeeUuid = response.data[0]
        }
        if (response.data.error) {
          return response.data
        }
        store.commit('log/newWorkLog', {type: 'EMPLOYEE_CREATE', value: EmployeeUuid})
        return EmployeeUuid
      })
      .catch(error => {
        store.commit('log/newError', {type: 'ERROR', value: error.response.data})
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
        EventBus.$emit('employee-changed')
        return response
      })
      .catch(error => {
        EventBus.$emit('employee-changed')
        store.commit('log/newError', {type: 'ERROR', value: error.response})
        return error.response
      })
  },

  create (create) {
    return this.createEntry(create)
      .then(response => {
        if (response.data.error) {
          return response.data
        }
        store.commit('log/newWorkLog', {type: 'EMPLOYEE_CREATE', value: response.data})
        return response.data
      })
  },

  leave (leave) {
    return this.createEntry(leave)
      .then(response => {
        if (response.data.error) {
          return response.data
        }
        store.commit('log/newWorkLog', {type: 'EMPLOYEE_LEAVE', value: response.data})
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
        EventBus.$emit('employee-changed')
        store.commit('log/newWorkLog', {type: 'EMPLOYEE_EDIT', value: response.data})
        return response.data
      })
      .catch(error => {
        store.commit('log/newError', {type: 'ERROR', value: error.response.data})
        return error.response.data
      })
  },

  move (move) {
    return this.edit(move)
      .then(response => {
        store.commit('log/newWorkLog', {type: 'EMPLOYEE_MOVE', value: response})
        return response
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
        return error.response
      })
  }
}
