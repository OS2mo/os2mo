import { Selector } from 'testcafe'
import { baseURL } from './support'

fixture('Login')
  .page(`${baseURL}/login/`)

test('Test empty login', async t => {
  await t
    .click('button[type="submit"]')
    .expect(Selector('.alert-danger').exists).notOk(
      'Empty login failed!'
    )
})

test('Test successful login', async t => {
  await t
    .typeText('input[name="username"]', 'Bendtner')
    .typeText('input[name="password"]', '12345')
    .click('button[type="submit"]')
    .expect(Selector('.alert-danger').exists).notOk(
      'Login failed!'
    )
})
