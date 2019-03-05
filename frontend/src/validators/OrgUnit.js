import Validate from '@/api/Validate'

export default {
  validate (value, args) {
    let validity = args[0]
    let orgUuid = args[1]

    if (!orgUuid) {
      return true
    }

    return Validate.orgUnit(orgUuid, validity)
  },

  getMessage (value, args, data) {
    return data
  }
}
