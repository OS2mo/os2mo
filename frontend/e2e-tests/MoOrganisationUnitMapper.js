import { ClientFunction, Selector } from 'testcafe'
import { baseURL } from './support'
import VueSelector from 'testcafe-vue-selectors'

let moment = require('moment')

fixture('MoOrganisationUnitMapper')
  .page(`${baseURL}`)

const mapperButton = Selector('button.btn-mapper')
const saveButton = Selector('button.btn-submit')

const headerText = Selector('h3').withText('Organisationssammenkobling')

const trees = VueSelector('mo-tree-view')
const leftTree = trees.filter('.origin')
const rightTree = trees.filter('.destination')

const leftNodes = leftTree.find('.tree-node .tree-content')
const rightNodes = rightTree.find('.tree-node .tree-content')

const reload = ClientFunction(() => window.location.reload())
const getPagePath = ClientFunction(() => window.location.pathname);

test('View no mapping', async t => {
  await t
    .click(mapperButton)
    .expect(headerText.exists).ok()

  // has the URL changed?
    .expect(getPagePath()).eql('/organisationssammenkobling')

  // we have a left tree, but no right tree
    .expect(leftTree.exists, {timout: 3000}).ok()
    .expect(rightTree.exists).notOk()

    .expect(leftNodes.withText('Hjørring').exists, {timout: 3000}).ok()

  // ...and it's just empty
    .expect(leftTree.getVue(({ computed }) => computed.contents))
    .eql("> Hjørring")

    .click(leftNodes.withText('Hjørring'))

  // the right tree appears now that we selected something
    .expect(rightTree.exists, {timeout: 3000}).ok()

    .expect(rightTree.getVue(({ computed }) => computed.contents))
    .eql("> ~~~ Hjørring ~~~")

    .click(leftNodes.withText('Hjørring').find('.tree-arrow'))
    .click(leftNodes.withText('Borgmesterens Afdeling'))

  // selecting a unit doesn't reveal it in the right tree
    .expect(rightTree.getVue(({ computed }) => computed.contents))
    .eql("> Hjørring")

    .click(rightNodes.withText('Hjørring').find('.tree-arrow'))

  // but revealing it ensures that it's disabled!
    .expect(rightTree.getVue(({ computed }) => computed.contents))
    .eql({
      "Hjørring": [
        "> ~~~ Borgmesterens Afdeling ~~~",
        "> Skole og Børn",
        "Social og sundhed",
        "> Teknik og Miljø"
      ]
    })
})


test('Writing mapping', async t => {
  await t
    .click(mapperButton)
    .expect(headerText.exists).ok()

    .expect(leftTree.exists, {timout: 3000}).ok()
    .click(leftNodes.withText('Hjørring'), {timout: 3000})
    .expect(rightTree.exists, {timeout: 3000}).ok()

    .expect(rightTree.getVue(({ computed }) => computed.contents))
    .eql("> ~~~ Hjørring ~~~")

    .expect(saveButton.getAttribute('disabled')).ok()

    .click(rightNodes.withText('Hjørring').find('.tree-arrow'))
    .click(rightNodes.withText('Teknik og Miljø').find('.tree-arrow'))
    .click(rightNodes.withText('Belysning').find('.tree-arrow'))
    .click(rightNodes.withText('IT-Support').find('.tree-arrow'))

    .expect(rightTree.getVue(({ computed }) => computed.contents))
    .eql({
      "~~~ Hjørring ~~~": [
        "> Borgmesterens Afdeling",
        "> Skole og Børn",
        "Social og sundhed",
        {
          "Teknik og Miljø": [
            {
              "Belysning": [
                "Kantine"
              ]
            },
            {
              "IT-Support": [
                "Kantine"
              ]
            },
            "Kloakering",
            "Park og vej",
            "Renovation"
          ]
        }
      ]
    })

    .click(rightNodes.withText('Kantine').nth(0))
    .click(rightNodes.withText('Kantine').nth(1))

    .expect(rightTree.getVue(({ computed }) => computed.contents))
    .eql({
      "~~~ Hjørring ~~~": [
        "> Borgmesterens Afdeling",
        "> Skole og Børn",
        "Social og sundhed",
        {
          "Teknik og Miljø": [
            {
              "Belysning": [
                "\u2713 Kantine"
              ]
            },
            {
              "IT-Support": [
                "\u2713 Kantine"
              ]
            },
            "Kloakering",
            "Park og vej",
            "Renovation"
          ]
        }
      ]
    })

    .expect(saveButton.getAttribute('disabled')).notOk()

    .click(saveButton)

  // FIXME: we should disable the button after a save
    // .expect(saveButton.getAttribute('disabled')).ok()

  // reload the page
    .expect(reload()).notOk()

  // assert that the selection has reset
    .expect(leftTree.exists, {timout: 3000}).ok()
    .expect(leftNodes.withText('Hjørring').exists).ok()

    .expect(leftTree.getVue(({ computed }) => computed.contents))
    .eql("> Hjørring")

  // assert that the selection has reset
    .click(leftNodes.withText('Hjørring'), {timout: 3000})
    .expect(rightTree.exists, {timeout: 3000}).ok()

    .expect(rightNodes.withText('Kantine').exists).ok()
    .expect(rightTree.getVue(({ computed }) => computed.contents))
    .eql({
      "~~~ Hjørring ~~~": [
        "> Borgmesterens Afdeling",
        "> Skole og Børn",
        "Social og sundhed",
        {
          "Teknik og Miljø": [
            {
              "Belysning": [
                "\u2713 Kantine"
              ]
            },
            {
              "IT-Support": [
                "\u2713 Kantine"
              ]
            },
            "Kloakering",
            "Park og vej",
            "Renovation"
          ]
        }
      ]
    })
})
