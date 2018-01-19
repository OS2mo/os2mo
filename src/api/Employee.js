import {HTTP} from './HttpCommon'

export default {

  /**
   * Get a list of all employees
   * @returns {Array} List of all employees
   */
  getAll () {
    return HTTP.get('/e/')
      .then(response => {
        return response.data
      })
  },

  /**
   * Get an employee
   * @param {String} uuid - uuid for employee
   * @returns {Object} employee object
   */
  getEmployee (uuid) {
    return HTTP.get(`/e/${uuid}`)
    .then(response => {
      return response.data
    })
    .catch(e => {
      console.log(e)
    })
  },

  /**
   * find an employee
   * @param {String} query -  search query
   * @return {Object}
   */
  searchForEmployee (query) {
    return HTTP.get(`/e/?limit=200&query=${query}&start=0`)
    .then(response => {
      return response.data
    })
  },

  /**
   * Get engagement details for employee
   * @param {String} uuid - employee uuid
   * @see getDetails
   */
  getEngagementDetails (uuid) {
    return this.getDetails(uuid, 'engagement')
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
   * Get it details for employee
   * @param {String} uuid - Employee uuid
   * @see getDetails
   */
  getItDetails (uuid) {
    return this.getDetails(uuid, 'it')
  },

  /**
   * Base call for getting details about an employee.
   * @param {String} uuid - Employee uuid
   * @param {String} detail - Name of the detail to get
   * @param {String} validity - Can be 'past', 'present' or 'future'
   * @returns {Object} Detail data
   */
  getDetails (uuid, detail, validity) {
    validity = validity || 'present'
    return HTTP.get(`/e/${uuid}/role-types/${detail}/?validity=${validity}`)
    .then(response => {
      return response.data
    })
  }
}
