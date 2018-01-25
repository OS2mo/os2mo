import {HTTP, Service} from './HttpCommon'

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
   * Create a new employee
   * @param {Object} engagement - new Employee uuid
   * @returns {Object} employee uuid
   */
  createEmployee (uuid, engagement) {
    return Service.post(`/e/${uuid}/create`, engagement)
    .then(response => {
      return response.data
    })
  },

  /**
   * Move an employee
   * @param {Object} uuid - employee to move
   * @param {String} engagement - uuid for the new employee
   * @returns {Object} employeee uuid
   */
  editEmployee (uuid, engagement) {
    return Service.post(`/e/${uuid}/edit`, engagement)
    .then(response => {
      return response.data
    })
  },

   /**
   * End an employee
   * @param {Object} engagement - the employee to end
   * @param {String} endDate - the date on which the employee shall end
   * @returns {Object} employee uuid
   */
  endEmployee (uuid, engagement) {
    return Service.post(`/e/${uuid}/terminate`, engagement)
    .then(response => {
      return response.data
    })
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
  },

  /**
   * Create a new engagement for an employee
   * @param {String} uuid - Employee uuid
   * @param {Object} engagement - New engagement
   */
  createEngagement (uuid, engagement) {
    return HTTP.post(`/e/${uuid}/roles/engagement`, engagement)
    .then(response => {
      console.log(response)
      return response
    })
  }
}
