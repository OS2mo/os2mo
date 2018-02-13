// https://gist.github.com/nicbell/6081098

export default {
  methods: {
    convertValidityDates (response) {
      response.forEach(e => {
        if (e.validity.from !== null) e.validity.from = new Date(e.validity.from)
        if (e.validity.to !== null) e.validity.to = new Date(e.validity.to)
      })
    }
  }
}
