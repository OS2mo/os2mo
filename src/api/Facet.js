import { Service } from './HttpCommon'

export default {
  /**
   * Get a list of all available facets
   * @param {String} uuid - organisation uuid
   * @returns {Array} a list of all available facets
   */
  getAll (uuid) {
    return this.getFacet(uuid)
  },

   /**
   * Get address types
   * @param {String} uuid - organisation uuid
   * @see getFacet
   */
  addressTypes (uuid) {
    return this.getFacet(uuid, 'address_type')
  },

  /**
   * Get association types
   * @param {String} uuid - organisation uuid
   * @see getFacet
   */
  associationTypes (uuid) {
    return this.getFacet(uuid, 'association_type')
  },

  /**
   * Get engagement types
   * @param {String} uuid - organisation uuid
   * @see getFacet
   */
  engagementTypes (uuid) {
    return this.getFacet(uuid, 'engagement_type')
  },

  /**
   * Get job functions
   * @param {String} uuid - organisation uuid
   * @see getFacet
   */
  jobFunctions (uuid) {
    return this.getFacet(uuid, 'job_function')
  },

  /**
   * Get organisation unit types
   * @param {String} uuid - organisation uuid
   * @see getFacet
   */
  organisationUnitTypes (uuid) {
    return this.getFacet(uuid, 'org_unit_type')
  },

  /**
   * Get role types
   * @param {String} uuid - organisation uuid
   * @see getFacet
   */
  roleTypes (uuid) {
    return this.getFacet(uuid, 'role_type')
  },

  /**
   * Base call for getting a facet
   * @param {String} uuid - organisation uuid
   * @param {String} facet - facet name
   * @returns {Array} a list of available facet options
   */
  getFacet (uuid, facet) {
    return Service.get(`/o/${uuid}/f/${facet}`)
    .then(response => {
      return response.data
    })
  }
}
