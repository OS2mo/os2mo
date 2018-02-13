import {HTTP, Service} from './HttpCommon'
import { EventBus } from '../EventBus'

export default {

  /**
   * Get a list of all employees
   * @returns {Array} List of all employees
   */
  getAll (orgUuid) {
    return Service.get(`/o/${orgUuid}/e/`)
      .then(response => {
        return response.data
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
  getEmployee (uuid) {
    return Service.get(`/e/${uuid}/`)
    .then(response => {
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  },

  /**
   * Get engagement details for employee
   * @param {String} uuid - employee uuid
   * @see getDetail
   */
  getEngagementDetails (uuid) {
    return this.getDetail(uuid, 'engagement')
  },

  /**
   * Get contacts details for employee
   * @param {String} uuid - Employee uuid
   * @see getDetails
   */
  getContactDetails (uuid) {
    return this.getDetails(uuid, 'contact')
  },

  /**
   * Get role details for employee
   * @param {String} uuid - Employee uuid
   * @see getDetail
   */
  getRoleDetails (uuid) {
    return this.getDetail(uuid, 'role')
  },

  /**
   * Get it details for employee
   * @param {String} uuid - Employee uuid
   * @see getDetail
   */
  getItDetails (uuid) {
    return this.getDetail(uuid, 'it')
  },

  /**
   * Base call for getting details.
   * @param {String} uuid - employee uuid
   * @param {String} detail - Name of the detail
   * @returns {Array} A list of options for the detail
   */
  getDetail (uuid, detail) {
    return Service.get(`/e/${uuid}/details/${detail}`)
    .then(response => {
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  },

  /**
   * Get a list of available details
   * @param {String} uuid - employee uuid
   * @returns {Object} A list of available tabs
   */
  getDetailList (uuid) {
    return Service.get(`e/${uuid}/details/`)
    .then(response => {
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  },

  /**
   * Base call for getting details about an employee.
   * @param {String} uuid - Employee uuid
   * @param {String} detail - Name of the detail to get
   * @param {String} validity - Can be 'past', 'present' or 'future'
   * @returns {Object} Detail data
   * @deprecated
   */
  getDetails (uuid, detail, validity) {
    validity = validity || 'present'
    return HTTP.get(`/e/${uuid}/role-types/${detail}/?validity=${validity}`)
    .then(response => {
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  },

  /**
   * Create a new employee
   * @param {String} uuid - employee uuid
   * @param {Array} create - A list of elements to create
   * @returns {Object} employee uuid
   */
  createEmployee (uuid, create) {
    return Service.post(`/e/${uuid}/create`, create)
    .then(response => {
      EventBus.$emit('employee-changed', response.data)
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  },

  /**
   * Move an employee
   * @param {String} uuid - employee uuid
   * @param {Array} edit - A list of elements to edit
   * @returns {Object} employeee uuid
   */
  editEmployee (uuid, edit) {
    return Service.post(`/e/${uuid}/edit`, edit)
    .then(response => {
      EventBus.$emit('employee-changed', response.data)
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  },

   /**
   * End an employee
   * @param {String} uuid - employee uuid
   * @param {Object} end - Object containing the end date
   * @returns {Object} employee uuid
   */
  endEmployee (uuid, end) {
    return Service.post(`/e/${uuid}/terminate`, end)
    .then(response => {
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  }
}
