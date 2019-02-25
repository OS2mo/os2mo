import { Selector } from 'testcafe'
import { baseURL } from './support'
import VueSelector from 'testcafe-vue-selectors'

let moment = require('moment')

fixture('MoEmployeeTerminate')
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

test('Workflow: terminate employee by search', async t => {
  let today = moment()

  await t
    .hover('#mo-workflow', { offsetX: 10, offsetY: 180 })
    .click('.btn-employee-terminate')

    .expect(dialog.exists).ok('Opened dialog')

    .click(searchEmployeeField)
    .typeText(searchEmployeeInput, 'thejs')

    // FIXME: this is wrong...
    .expect(searchEmployeeInput.value)
    .eql('hejs', 'Have you fixed a bug so that it retains the first letter?')

    .expect(searchEmployeeItem.withText(' ').visible).ok()
    .pressKey('down enter')
    .expect(searchEmployeeInput.value).eql('Thejs Hvid Larsen')

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

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
    .typeText(mainSearchField, 'holdg')
    .expect(mainSearchInput.value)
    .eql('holdg')
    .expect(mainSearchItem.withText(' ').visible).ok()
    .pressKey('down enter')
    .expect(mainSearchInput.value)
    .eql('Alex Holdgaard Hansen')

    .expect(fromField.innerText)
    .eql('01-08-1971')
    .expect(toField.innerText)
    .eql('')

    .hover('#mo-workflow', { offsetX: 10, offsetY: 180 })
    .click('.btn-employee-terminate')

    .expect(dialog.exists).ok('Opened dialog')

    // TODO: we shouldn't need to fill in the employee
    .click(searchEmployeeField)
    .typeText(searchEmployeeInput, 'holdg')
    .expect(searchEmployeeItem.withText(' ').visible).ok()
    .pressKey('down enter')
    .expect(searchEmployeeInput.value).eql('Alex Holdgaard Hansen')

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    .click(dialog.find('.btn-primary'))

    .expect(dialog.exists).notOk()

    .expect(VueSelector('MoLog')
      .find('.alert').nth(-1).innerText)
    .match(
      /Medarbejderen med UUID [-0-9a-f]* er afsluttet/
    )

    .expect(fromField.innerText)
    .eql('01-08-1971')
    .expect(toField.innerText)
    .eql(today.format('DD-MM-YYYY'))
})

test('Workflow: terminate employee role', async t => {
  const today = moment()
  const expectedTerminationDate = today.format('DD-MM-YYYY')
  const entryModal = VueSelector('mo-entry-terminate-modal')
  const terminateDialog = entryModal.find('*[role=dialog]')

  const roleID = 'f0c6f0a4-db51-4c40-bd83-1267a667aa30'

  await t
    .click(mainSearchField)
    .typeText(mainSearchField, 'kolind')
    .expect(mainSearchItem.withText(' ').visible).ok()
    .pressKey('down enter')
    .expect(mainSearchInput.value).eql('Kim Kolind Christensen')

    .expect(fromField.innerText)
    .eql('13-07-1986')
    .expect(toField.innerText)
    .eql('')

    .click(VueSelector('employee-detail-tabs bTabButtonHelper')
           .withText('Roller'))

    .expect(fromField.innerText)
    .eql('13-07-1986')
    .expect(toField.innerText)
    .eql('')

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
    .eql('13-07-1986')
    .expect(toField.innerText)
    .eql(expectedTerminationDate)

    .expect(VueSelector('MoLog')
      .find('.alert').nth(-1).innerText)
    .eql(
      `Rolle med UUID ${roleID} er blevet afsluttet pr. ${today.format('YYYY-MM-DD')}.`
    )
})
