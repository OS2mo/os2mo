import { Selector } from 'testcafe'
import { baseURL } from './support'
import VueSelector from 'testcafe-vue-selectors'

let moment = require('moment')

const ROOTID = '97337de5-6096-41f9-921e-5bed7a140d85'

const dialog = Selector('#employeeCreate')

// CPR Number
const checkbox = Selector('input[data-vv-as="checkbox"]')

// Engagement
const engagementCheckbox = dialog.find('.container')

const parentEngagementInput = dialog.find('input[data-vv-as="Angiv enhed"]')

const jobFunctionEngagementSelect = dialog.find('select[data-vv-as="Stillingsbetegnelse"]')
const jobFunctionEngagementOption = jobFunctionEngagementSelect.find('option')

const engagementTypeSelect = dialog.find('select[data-vv-as="Engagementstype"]')
const engagementTypeOption = engagementTypeSelect.find('option')

const fromInput = dialog.find('.from-date input.form-control')

// Address
const addressTypeSelect = dialog.find('select[data-vv-as="Adressetype"]')
const addressTypeOption = addressTypeSelect.find('option')

const addressInput = dialog.find('input[data-vv-as="Tlf"]')

const addressVisibility = dialog.find('select[data-vv-as="Synlighed"]')
const addressVisibilityOption = addressVisibility.find('option')

// Association
const associationCheckbox = dialog.find('[data-vv-as="Primær tilknytning"] .container')

const parentAssociationInput = dialog.find('.unit-association input[data-vv-as="Angiv enhed"]')

const addressAssociationSelect = dialog.find('.address-association select[data-vv-as="Adresser"]')

const associationTypeSelect = dialog.find('.select-association select[data-vv-as="Tilknytningsrolle"]')
const associationTypeOption = associationTypeSelect.find('option')

// Role
const parentRoleInput = dialog.find('.unit-role input[data-vv-as="Angiv enhed"]')

const roleTypeSelect = dialog.find('.select-role select[data-vv-as="Rolletype"]')
const roleTypeOption = roleTypeSelect.find('option')

// IT System
const itSystemSelect = dialog.find('.select-itSystem select[data-vv-as="IT systemer"]')
const itSystemOption = itSystemSelect.find('option')
const itSystemInput = dialog.find('.input-itSystem input[data-vv-as="Kontonavn"]')

// Manager
const parentManagerInput = dialog.find('.unit-manager input[data-vv-as="Angiv enhed"]')

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

const treeNodes = Selector('.tree-node .tree-content')

// Search field
const searchField = Selector('.search-bar')
const searchFieldItem = searchField.find('.v-autocomplete-list-item')

fixture('MoEmployeeCreate')
  .page(`${baseURL}/medarbejder/liste`)

test('Workflow: create employee', async t => {
  let today = moment()

  await t
    .hover('#mo-workflow', { offsetX: 10, offsetY: 10 })
    .click('.btn-employee-create')

    .expect(dialog.exists).ok('Opened dialog')

    // CPR Number
    .typeText(dialog.find('input[data-vv-as="CPR nummer"]'), '2003920008')
    .click(dialog.find('.btn-outline-primary'))
    .click(checkbox)
    .expect(checkbox.checked).ok()

    // Engagement
    .click(engagementCheckbox)

    .click(parentEngagementInput)
    .expect(dialog.find('span.tree-anchor').exists)
    .ok()
    .click(dialog.find('span.tree-anchor'))

    .click(jobFunctionEngagementSelect)
    .click(jobFunctionEngagementOption.withText('Specialist'))

    .click(engagementTypeSelect)
    .click(engagementTypeOption.withText('Ansat'))

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    // Address
    .click(dialog.find('.btn-address .btn-outline-success'))

    .click(addressTypeSelect)
    .click(addressTypeOption.withText('Tlf'))

    .click(addressInput)
    .typeText(addressInput, '35502010')

    .click(addressVisibility)
    .click(addressVisibilityOption.nth(1))

    // Association
    .click(dialog.find('.btn-association .btn-outline-success'))

    .click(associationCheckbox)

    .click(parentAssociationInput)
    .click(dialog.find('.unit-association span.tree-anchor'))

    .click(associationTypeSelect)
    .click(associationTypeOption.withText('Konsulent'))

    // Role
    .click(dialog.find('.btn-role .btn-outline-success'))

    .click(parentRoleInput)
    .click(dialog.find('.unit-role span.tree-anchor'))

    .click(roleTypeSelect)
    .click(roleTypeOption.withText('Tillidsrepræsentant'))

    // IT System
    .click(dialog.find('.btn-itSystem .btn-outline-success'))

    .click(itSystemSelect)
    .click(itSystemOption.withText('Active Directory'))
    .click(itSystemInput)
    .typeText(itSystemInput, 'chefen')

    // Manager
    .click(dialog.find('.btn-manager .btn-outline-success'))

    .click(parentManagerInput)
    .click(dialog.find('.unit-manager .tree-anchor'))

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
    .typeText(dialog.find('input[data-vv-as="Email"]'), 'hest@test.dk')

    .click(managerTypeSelect)
    .click(managerTypeOption.withText('Direktør'))

    .click(levelManagerSelect)
    .click(levelManagerOption.withText('Niveau 90'))

    .click(responsibilityManagerSelect)
    .click(responsibilityManagerOption.withText('Beredskabsledelse'))

    // Submit button
    .click(dialog.find('.btn-primary'))

    .expect(dialog.exists).notOk()

    .expect(VueSelector('MoLog')
      .find('.alert').nth(0).innerText)
    .match(
      /Medarbejderen med UUID [-0-9a-f]* er blevet oprettet/
    )
    // Verify that we can search for the newly created employee
    .click(searchField)
    .typeText(searchField.find('input'), 'sig')
    .expect(searchFieldItem.withText('Signe Kristensen').visible).ok()
})

test('Workflow: create employee with role only', async t => {
  let today = moment()

  await t
    .hover('#mo-workflow', { offsetX: 10, offsetY: 10 })
    .click('.btn-employee-create')

    .expect(dialog.exists).ok('Opened dialog')

    // CPR Number
    .typeText(dialog.find('input[data-vv-as="CPR nummer"]'), '2003920009')
    .click(dialog.find('.btn-outline-primary'))
    .click(checkbox)
    .expect(checkbox.checked).ok()

    // Engagement
    .click(parentEngagementInput)
    .click(dialog.find('span.tree-anchor'))

    .click(jobFunctionEngagementSelect)
    .click(jobFunctionEngagementOption.withText('Skolepsykolog'))

    .click(engagementTypeSelect)
    .click(engagementTypeOption.withText('Ansat'))

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    // Role
    .click(dialog.find('.btn-role .btn-outline-success'))

    .click(parentRoleInput)
    .click(dialog.find('.unit-role span.tree-anchor'))

    .click(roleTypeSelect)
    .click(roleTypeOption.withText('Tillidsrepræsentant'))

    // Submit button
    .click(dialog.find('.btn-primary'))

    .expect(dialog.exists).notOk()

    .expect(VueSelector('MoLog')
      .find('.alert').nth(-1).innerText)
    .match(
      /Medarbejderen med UUID [-0-9a-f]* er blevet oprettet/
    )
    .expect(Selector('.card-title').textContent)
    .match(/Oliver Jensen \(200392-0009\)/)
    .click(VueSelector('bTabButtonHelper').withText('Roller'))
    .expect(Selector('ul.role_type-name').textContent)
    .match(/Tillidsrepræsentant/)
})

test('Workflow: create employee with association to unit lacking address', async t => {
  let today = moment()

  await t
    .hover('#mo-workflow', { offsetX: 10, offsetY: 10 })
    .click('.btn-employee-create')

    .expect(dialog.exists).ok('Opened dialog')

    // CPR Number
    .typeText(dialog.find('input[data-vv-as="CPR nummer"]'), '2003920010')
    .click(dialog.find('.btn-outline-primary'))
    .click(checkbox)
    .expect(checkbox.checked).ok()

    // Engagement
    .click(parentEngagementInput)
    .expect(dialog.find('span.tree-anchor').exists)
    .ok()
    .click(dialog.find('span.tree-anchor'))

    .click(jobFunctionEngagementSelect)
    .click(jobFunctionEngagementOption.withText('Skolepsykolog'))

    .click(engagementTypeSelect)
    .click(engagementTypeOption.withText('Ansat'))

    .click(fromInput)
    .hover(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .click(dialog.find('.vdp-datepicker .day:not(.blank)')
      .withText(today.date().toString()))
    .expect(fromInput.value).eql(today.format('DD-MM-YYYY'))

    // Association
    .click(dialog.find('.btn-association .btn-outline-success'))

    .click(parentAssociationInput)
    .expect(dialog.find('.unit-association .tree-arrow').exists)
    .ok()
    .click(dialog.find('.unit-association .tree-arrow'), {offsetX: 0, offsetY: 0})
    .expect(dialog.find('.unit-association .tree-node .tree-content')
            .withText('Social og sundhed').exists)
    .ok()
    .click(dialog.find('.unit-association .tree-node .tree-content')
            .withText('Social og sundhed'))

    .click(associationTypeSelect)
    .click(associationTypeOption.withText('Konsulent'))

    // Submit button
    .click(dialog.find('.btn-primary'))

    .expect(dialog.exists).notOk()

    .expect(VueSelector('MoLog')
      .find('.alert').nth(-1).innerText)
    .match(
      /Medarbejderen med UUID [-0-9a-f]* er blevet oprettet/
    )

    // verify whom we created
    .expect(Selector('.card-title').textContent)
    .match(/Sarah Mortensen \(200392-0010\)/)

    // and the association
    .click(VueSelector('bTabButtonHelper').withText('Tilknytninger'))
    .expect(Selector('ul.association_type-name').textContent)
    .match(/Konsulent/)
})
