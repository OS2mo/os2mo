import { Selector } from 'testcafe'
import { baseURL } from './support'

let moment = require('moment')

fixture('Employee test')
  .page(`${baseURL}/medarbejder/liste`)

const dialog = Selector('#employeeMove')

const searchEmployeeInput = dialog.find('.search-employee .v-autocomplete[data-vv-as="Medarbejder"]')
const searchEmployeeItem = searchEmployeeInput.find('.v-autocomplete-list-item')

const engagementSelect = dialog.find('select[data-vv-as="Engagementer"]')
const engagementOption = engagementSelect.find('option')

const unitInput = dialog.find('.v-autocomplete[data-vv-as="Enhed"]')
const unitItem = unitInput.find('.v-autocomplete-list-item label')

const fromInput = dialog.find('.from-date input.form-control')

const checkbox = Selector('input[data-vv-as="checkbox"]')

test('Workflow: move employee', async t => {
  let today = moment()

  await t
    .setTestSpeed(0.8)
    .hover('#mo-workflow', {offsetX: 10, offsetY: 100})
    .click('.btn-employee-move')

    .expect(dialog.exists).ok('Opened dialog')

    .click(searchEmployeeInput)
    .typeText(searchEmployeeInput.find('input'), 'sune')
    .expect(searchEmployeeItem.withText('Sune Skriver').visible).ok()
    .pressKey('down enter')
    .expect(searchEmployeeInput.find('input').value).eql('Sune Skriver')

    .click(engagementSelect)
    .click(engagementOption.withText('Ansat, Ballerup Kommune'))

    .click(unitInput)
    .typeText(unitInput.find('input'), 'fam')
    .expect(unitItem.withText('Ballerup Familiehus').visible).ok()
    .pressKey('down enter')
    .expect(unitInput.find('input').value).eql('Ballerup Familiehus')

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    .click(checkbox)
    .expect(checkbox.checked).ok()

    .click(dialog.find('.btn-primary'))

    .expect(Selector('#employeeTerminate').exists).notOk()

    // Running the test second time
    .hover('#mo-workflow', {offsetX: 10, offsetY: 100})
    .click('.btn-employee-move')

    .expect(dialog.exists).ok('Opened dialog')

    .click(searchEmployeeInput)
    .typeText(searchEmployeeInput.find('input'), 'sune')
    .expect(searchEmployeeItem.withText('Sune Skriver').visible).ok()
    .pressKey('down enter')
    .expect(searchEmployeeInput.find('input').value).eql('Sune Skriver')

    .click(engagementSelect)
    .click(engagementOption.withText('Ansat, Ballerup Familiehus'))

    .click(unitInput)
    .typeText(unitInput.find('input'), 'kom')
    .expect(unitItem.withText('Ballerup Kommune').visible).ok()
    .pressKey('down enter')
    .expect(unitInput.find('input').value).eql('Ballerup Kommune')

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
           .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    .click(checkbox)
    .expect(checkbox.checked).ok()

    .click(dialog.find('.btn-primary'))

    .expect(Selector('#employeeTerminate').exists).notOk()
})
