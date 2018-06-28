import { baseURL } from './support'

fixture('Getting Started')
  .page(`${baseURL}/login/`)

test('My first test', async t => {
  await t
    .click('.btn-text')
    .typeText('input[name="username"]', 'Bendtner')
    .typeText('input[name="password"]', '12345')
    .click('button[type="submit"]')
})
