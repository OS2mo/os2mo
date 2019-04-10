import VueSelector from 'testcafe-vue-selectors'
import { Selector } from 'testcafe'
import { baseURL, reset } from './support'

let moment = require('moment')

fixture('MoOrganisationManagerTab')
  .beforeEach(reset)
  .page(`${baseURL}/organisation/a6773531-6c0a-4c7b-b0e2-77992412b610`)

const dialog = Selector('.modal-content')

// Manager
const searchManagerEmployee = dialog.find('.v-autocomplete[data-vv-as="Medarbejder"]')
const searchManagerItem = searchManagerEmployee.find('.v-autocomplete-list-item')

const managerTypeSelect = dialog.find('.select-manager select[data-vv-as="Ledertype"]')
const managerTypeOption = managerTypeSelect.find('option')

const levelManagerSelect = dialog.find('.select-manager select[data-vv-as="Lederniveau"]')
const levelManagerOption = levelManagerSelect.find('option')

const responsibilityManagerSelect = dialog.find('.responsibility-manager select[data-vv-as="Lederansvar"]')
const responsibilityManagerOption = responsibilityManagerSelect.find('option')

const fromRemoveInput = dialog.find('.vdp-datepicker__clear-button')
const fromInput = dialog.find('.from-date input.form-control')

test('Workflow: organisation manager tab', async t => {
  let today = moment()

  await t
    .expect(Selector('.row .user-settings')
      .find('.card-text .orgunit-location').innerText)
    .match(
      /Hjørring Kommune/
    )
    .expect(Selector('.row .user-settings')
      .find('.card-text .orgunit-user_key').innerText)
    .match(
      /Social og sundhed/
    )

    .click(VueSelector('organisation-detail-tabs bTabButtonHelper').withText('Ledere'))


    // Create manager
    .click(Selector('.btn-outline-primary').withText('Opret ny'))

    .click(managerTypeSelect)
    .click(managerTypeOption.withText('Direktør'))

    .click(levelManagerSelect)
    .click(levelManagerOption.withText('Niveau 3'))

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
    .typeText(searchManagerEmployee.find('input'), 'jens')

    .expect(searchManagerItem.withText(' ').visible).ok()
    .pressKey('down enter')
    .expect(searchManagerEmployee.find('input').value).match(/Jens/)

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

