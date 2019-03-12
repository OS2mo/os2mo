import Validate from '@/api/Validate'

export default {
  validate (value, args) {
    let orgUnit = args[0]
    let parent = args[1]
    let validity = args[2]

    // A plethora of null and false checks to stop everything from breaking
    if (!validity || !validity.from) {
      return true
    }

    return Validate.candidateParentOrgUnit(orgUnit, parent, validity)
  },

  getMessage (value, args, data) {
    return data
  }
}
