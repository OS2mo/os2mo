import { Selector } from 'testcafe'
import { baseURL } from './support'

fixture('Login')
  .page(`${baseURL}/login/`)

test('Test empty login', async t => {
  await t
    .click(Selector('.btn-text').withText('Organisation'))
    .expect(Selector('#login.modal').exists).ok(
      'Login dialog failed to appear'
    )
    .click('button[type="submit"]')
    .expect(Selector('.alert-danger').exists).notOk(
      'Empty login failed!'
    )
    .expect(Selector('#login.modal').exists).notOk(
      'Login dialog failed to disappear'
    )
})

test('Test successful login', async t => {
  await t
    .click(Selector('.btn-text').withText('Organisation'))
    .expect(Selector('#login.modal').exists).ok(
      'Login dialog failed to appear'
    )
    .typeText('input[name="username"]', 'Bendtner')
    .typeText('input[name="password"]', '12345')
    .click('button[type="submit"]')
    .expect(Selector('.alert-danger').exists).notOk(
      'Login failed!'
    )
    .expect(Selector('#login.modal').exists).notOk(
      'Login dialog failed to disappear'
    )
})
