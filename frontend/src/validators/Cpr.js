import Validate from '@/api/Validate'

export default {
  validate (value, orgUuid) {
    return Validate.cpr(value, orgUuid)
  },

  getMessage (value, args, data) {
    return data
  }
}
