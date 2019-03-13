import fetch from 'node-fetch'

export let baseURL = process.env.BASE_URL ?
  process.env.BASE_URL.replace(/\/+$/, '') : 'http://localhost:8080'

export async function reset(test) {
  await fetch(baseURL + '/reset-db')
}
