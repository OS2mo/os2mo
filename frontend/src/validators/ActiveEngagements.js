import Validate from '@/api/Validate'

export default {
  validate (value, args) {
    let validity = args[0]
    let employee = value

    // A plethora of null and false checks to stop everything from breaking
    if (!validity || !validity.from ||
      Object.keys(employee).length === 0 || !employee) {
      return true
    }

    return Validate.activeEngagements(employee, validity)
  },

  getMessage (value, args, data) {
    return data
  }
}
