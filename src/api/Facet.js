import { Service } from './HttpCommon'

export default {

  /**
   * Get IT a list of available IT systems
   * @param {String} uuid - organisation uuid
   * @returns {Array} a list of options
   */
  itSystems (uuid) {
    return Service.get(`/o/${uuid}/it/`)
    .then(response => {
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  },

  /**
   * Get a list of options for a facet
   * @param {String} uuid - organisation uuid
   * @returns {Array} a list of options
   */
  getFacet (uuid, facet) {
    return Service.get(`/o/${uuid}/f/${facet}/`)
    .then(response => {
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  },

  /**
   * Get a list of all available facets
   * @param {String} uuid - organisation uuid
   * @see getFacet
   */
  getAll (uuid) {
    return this.getFacet(uuid)
  },

  /**
   * Return a list of organisation unit type options
   * @param {String} uuid - organisation uuid
   * @see getFacet
   */
  organisationUnitTypes (uuid) {
    return this.getFacet(uuid, 'org_unit_type')
  },

  /**
   * Return a list of address type options
   * @param {String} uuid - organisation uuid
   * @see getFacet
   */
  addressTypes (uuid) {
    return this.getFacet(uuid, 'address_type')
  },

  /**
   * Return a list of role type options
   * @param {String} uuid - organisation uuid
   * @see getFacet
   */
  roleTypes (uuid) {
    return this.getFacet(uuid, 'role_type')
  },

  /**
   * Return a list of association type options
   * @param {String} uuid - organisation uuid
   * @see getFacet
   */
  associationTypes (uuid) {
    return this.getFacet(uuid, 'association_type')
  },

  /**
   * Return a list of engagement type options
   * @param {String} uuid - organisation uuid
   * @see getFacet
   */
  engagementTypes (uuid) {
    return this.getFacet(uuid, 'engagement_type')
  },

  /**
   * Return a list of job function options
   * @param {String} uuid - organisation uuid
   * @see getFacet
   */
  jobFunctions (uuid) {
    return this.getFacet(uuid, 'job_function')
  },

   /**
   * Return a list of leave type options
   * @param {String} uuid - organisation uuid
   * @see getFacet
   */
  leaveTypes (uuid) {
    return this.getFacet(uuid, 'leave_type')
  }
}
