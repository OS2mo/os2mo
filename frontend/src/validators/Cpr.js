import Validate from '@/api/Validate'

export default {
  validate (value, orgUuid) {
    return Validate.cpr(value, orgUuid)
  },

  getMessage (value, args) {
    return 'CPR nummeret er allerede i brug'
  }
}
