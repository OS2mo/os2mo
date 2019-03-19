import VueSelector from 'testcafe-vue-selectors'
import { Selector } from 'testcafe'
import { baseURL } from './support'

let moment = require('moment')

fixture('MoOrganisationManagerTab')
  .page(`${baseURL}/organisation/40644200-b3f1-42d4-8752-8dab581d5b23`)

const dialog = Selector('.modal-content')

// Manager
const searchManagerEmployee = dialog.find('.v-autocomplete[data-vv-as="Medarbejder"]')
const searchManagerItem = searchManagerEmployee.find('.v-autocomplete-list-item')

const addressManagerTypeSelect = dialog.find('.address-manager select[data-vv-as="Adressetype"]')
const addressManagerTypeOption = addressManagerTypeSelect.find('option')

const addressManagerInput = dialog.find('.address-manager .v-autocomplete[data-vv-as="Adresse"]')
const addressManagerItem = addressManagerInput.find('.v-autocomplete-list-item label')

const managerTypeSelect = dialog.find('.select-manager select[data-vv-as="Ledertype"]')
const managerTypeOption = managerTypeSelect.find('option')

const addressManagerMany = dialog.find('.address-manager button')

const addressManagerInputEmail = dialog.find('input[data-vv-as="Email"]')

const levelManagerSelect = dialog.find('.select-manager select[data-vv-as="Lederniveau"]')
const levelManagerOption = levelManagerSelect.find('option')

const responsibilityManagerSelect = dialog.find('.responsibility-manager select[data-vv-as="Lederansvar"]')
const responsibilityManagerOption = responsibilityManagerSelect.find('option')

const fromRemoveInput = dialog.find('.vdp-datepicker__clear-button')
const fromInput = dialog.find('.from-date input.form-control')

test('Workflow: organisation manager tab', async t => {
  let today = moment()

  await t
    .click(VueSelector('organisation-detail-tabs bTabButtonHelper').withText('Ledere'))

    // Create manager
    .click(Selector('.btn-outline-primary').withText('Opret ny'))

    .click(addressManagerTypeSelect)
    .click(addressManagerTypeOption.nth(1))

    .click(addressManagerInput)
    .typeText(addressManagerInput.find('input'), 'baa')
    .expect(addressManagerItem.withText('Bålvej').visible)
    .ok()
    .pressKey('down down down down down down enter')
    .expect(addressManagerInput.find('input').value)
    .eql('Bålvej 1, 9800 Hjørring')

    .click(addressManagerMany)
    .pressKey('tab tab tab tab tab down down enter')

    .click(addressManagerInputEmail)
    .typeText(dialog.find('input[data-vv-as="Email"]'), 'magenta@test.dk')

    .click(managerTypeSelect)
    .click(managerTypeOption.withText('Direktør'))

    .click(levelManagerSelect)
    .click(levelManagerOption.withText('Niveau 90'))

    .click(responsibilityManagerSelect)
    .click(responsibilityManagerOption.withText('Beredskabsledelse'))

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))


    .click(dialog.find('.btn-primary'))

    .expect(dialog.exists).notOk()

    .expect(VueSelector('MoLog')
      .find('.alert').nth(0).innerText)
    .match(
      /Organisationsenheden med UUID [-0-9a-f]* er blevet oprettet/
    )

    // Edit manager
    .click(Selector('.edit-entry .btn-outline-primary'))

    .click(searchManagerEmployee)
    .typeText(searchManagerEmployee.find('input'), 'anne')
    .expect(searchManagerItem.withText(' ').visible).ok()
    .pressKey('down enter')
    .expect(searchManagerEmployee.find('input').value).eql('Anne  Andersen')

    .click(managerTypeSelect)
    .click(managerTypeOption.withText('Leder'))

    .click(levelManagerSelect)
    .click(levelManagerOption.withText('Niveau 1'))

    .click(fromRemoveInput)
    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    .click(dialog.find('.btn-primary'))

    .expect(dialog.exists).notOk()

    .expect(VueSelector('MoLog')
      .find('.alert').nth(0).innerText)
    .match(
      /Organisationsenheden med UUID [-0-9a-f]* er blevet redigeret/
    )

    // Terminate association
    .click(Selector('.terminate-entry .btn-outline-danger'))

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    .click(dialog.find('.btn-primary'))

    .expect(VueSelector('MoLog')
      .find('.alert').nth(0).innerText)
    .match(
      /Leder med UUID [-0-9a-f]* er blevet afsluttet pr./
    )
})

