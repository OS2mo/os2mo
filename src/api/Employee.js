import {HTTP} from './HttpCommon'

export default {

  /**
   * Get a list of all employees
   * @returns {Array} List of all employees
   */
  getAll () {
    return HTTP.get('/mo/e/')
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
    return HTTP.get('/mo/e/' + uuid)
    .then(response => {
      return response.data
    })
    .catch(e => {
      console.log(e)
    })
  },

  searchForEmployee (query) {
    return HTTP.get('/mo/e/?limit=200&query=' + query + '&start=0')
    .then(response => {
      return response.data
    })
  },

  getEngagementDetails (uuid) {
    return this.getDetails(uuid, 'engagement')
  },

  getContactDetails (uuid) {
    return this.getDetails(uuid, 'contact')
  },

  /**
   * Base call for getting details about an employee.
   * @param {String} uuid - Uuid for employee
   * @param {String} detail - Name of the detail to get
   * @param {String} validity - Can be 'past', 'present' or 'future'
   */
  getDetails (uuid, detail, validity) {
    validity = validity || 'present'
    return HTTP.get('/mo/e/' + uuid + '/role-types/' + detail + '/?validity=' + validity)
    .then(response => {
      return response.data
    })
  }
}
