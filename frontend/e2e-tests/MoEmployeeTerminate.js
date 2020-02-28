// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { Selector } from 'testcafe'
import { baseURL, setup, teardown } from './support'
import VueSelector from 'testcafe-vue-selectors'

let moment = require('moment')

fixture('MoEmployeeTerminate')
  .before(setup)
  .after(teardown)
  .page(`${baseURL}/medarbejder/liste`)

const dialog = Selector('#employeeTerminate')

const searchEmployeeField = dialog.find('.search-employee .v-autocomplete[data-vv-as="Medarbejder"]')
const searchEmployeeItem = searchEmployeeField.find('.v-autocomplete-list-item')
const searchEmployeeInput = searchEmployeeField.find('input')

const mainSearchField = VueSelector('mo-navbar v-autocomplete')
const mainSearchItem = mainSearchField.find('.v-autocomplete-list-item')
const mainSearchInput = mainSearchField.find('input')

const presentDetails = Selector('.tabs .detail-present')
const fromField = presentDetails.find('td.column-from')
const toField = presentDetails.find('td.column-to')

const fromInput = dialog.find('.from-date input.form-control')

const checkbox = Selector('input[data-vv-as="checkbox"]')

test('Workflow: terminate employee by search', async t => {
  let today = moment()

  await t
    .hover('#mo-workflow', { offsetX: 10, offsetY: 180 })
    .click('.btn-employee-terminate')

    .expect(dialog.exists).ok('Opened dialog')

    .click(searchEmployeeField)
    .typeText(searchEmployeeInput, 'Lis')

    .expect(searchEmployeeInput.value)
    .eql('Lis')

    .expect(searchEmployeeItem.withText(' ').visible)
    .ok('no user found - did test data change?')
    .pressKey('down enter')
    .expect(searchEmployeeInput.value).match(/Lis/)

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    .click(checkbox)
    .expect(checkbox.checked).ok()

    .click(dialog.find('.btn-primary'))

    .expect(dialog.exists).notOk()

    .expect(VueSelector('MoLog')
      .find('.alert').nth(-1).innerText)
    .match(
      /Medarbejderen med UUID [-0-9a-f]* er afsluttet/
    )
})

test('Workflow: terminate employee from page', async t => {
  let today = moment()

  await t
    .click(mainSearchField)
    .typeText(mainSearchField, 'erik')
    .expect(mainSearchInput.value)
    .eql('erik')
    .expect(mainSearchItem.withText(' ').visible).ok()
    .pressKey('down enter')
    .expect(mainSearchInput.value).match(/Erik/)

  let userID = await t.eval(() => window.location.pathname.split('/').slice(-1))
  let name = await mainSearchInput.value
  let fromDate = await fromField.innerText

  await t
    .expect(toField.innerText)
    .eql('')

    .hover('#mo-workflow', { offsetX: 10, offsetY: 180 })
    .click('.btn-employee-terminate')

    .expect(dialog.exists).ok('Opened dialog')

    // TODO: we shouldn't need to fill in the employee
    .click(searchEmployeeField)
    .typeText(searchEmployeeInput, 'erik')
    .expect(searchEmployeeItem.withText(' ').visible).ok()
    .pressKey('down enter')
    .expect(searchEmployeeInput.value).eql(name)

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    .click(checkbox)
    .expect(checkbox.checked).ok()

    .click(dialog.find('.btn-primary'))

    .expect(dialog.exists).notOk()

    .expect(VueSelector('MoLog')
      .find('.alert').nth(-1).innerText)
    .eql(`Medarbejderen med UUID ${userID} er afsluttet.`)

    .expect(fromField.innerText)
    .eql(fromDate)
    .expect(toField.innerText)
    .eql(today.format('DD-MM-YYYY'))
})

test('Workflow: terminate employee role', async t => {
  const today = moment()
  const expectedTerminationDate = today.format('DD-MM-YYYY')
  const entryModal = VueSelector('mo-entry-terminate-modal')
  const terminateDialog = entryModal.find('*[role=dialog]')

  await t
    .click(mainSearchField)
    .typeText(mainSearchField, 'Anders')
    .expect(mainSearchItem.withText(' ').visible).ok()
    .pressKey('down enter')
    .expect(mainSearchInput.value).match(/Anders/)

    .click(VueSelector('employee-detail-tabs bTabButtonHelper')
           .withText('Roller'))

  let fromDate = await fromField.innerText

  await t
    .expect(entryModal.count)
    .eql(1)

    .click(entryModal.find('button'))

    .expect(terminateDialog.visible)
    .ok()

    .click(entryModal.find('.from-date input'))

    .hover(entryModal.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .click(entryModal.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .expect(entryModal.find('.from-date input').value)
    .eql(expectedTerminationDate)

    .click(entryModal.find('button.btn-primary'))

    .expect(terminateDialog.exists)
    .notOk()

    .expect(fromField.innerText)
    .eql(fromDate)
    .expect(toField.innerText)
    .eql(expectedTerminationDate)

    .expect(VueSelector('MoLog')
      .find('.alert').nth(-1).innerText)
    .match(new RegExp(
      `Rolle med UUID [-0-9a-f]+ er blevet afsluttet pr. ${today.format('YYYY-MM-DD')}.`
    ))
})
