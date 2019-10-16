import { Selector } from 'testcafe'
import VueSelector from 'testcafe-vue-selectors'
import { baseURL, setup, reset, teardown } from './support';

const dialog = Selector('#orgUnitTerminate')

const trees = new Map([
  ["", [
    "> Hjørring Kommune",
    "> Lønorganisation"
  ]],
  ["f06ee470-9f17-566f-acbe-e938112d46d9", [
    "> =+= Hjørring Kommune =+=",
    "> Lønorganisation"
  ]],
  ["535ba446-d618-4e51-8dae-821d63e26560",  [
    {
      "Hjørring Kommune": [
        "> Borgmesterens Afdeling",
        {
          "Skole og Børn": [
            "IT-Support",
            "> Skoler og børnehaver",
            "=+= Social Indsats =+="
          ]
        },
        "Social og sundhed",
        "> Teknik og Miljø"
      ]
    },
    "> Lønorganisation"
  ]],
  ["96a4715c-f4df-422f-a4b0-9dcc686753f7", [
    {
        "Hjørring Kommune": [
            {
                "Borgmesterens Afdeling": [
                    "Budget og Planlægning",
                    "Byudvikling",
                    "Erhverv",
                    "=+= HR og organisation =+=",
                    "IT-Support"
                ]
            },
            "> Skole og Børn",
            "Social og sundhed",
            "> Teknik og Miljø"
        ]
    },
    "> Lønorganisation"
]
],
])

let tree = Selector('.orgunit-tree').with({ visibilityCheck: true})
let treeNode = tree.find('.tree-node')
let treeAnchor = treeNode.find('.tree-anchor')
let rootNode = treeNode.withText('Hjørring Kommune')
let selected = treeNode.filter('.selected')

let currentUnitName = Selector('.orgunit .orgunit-name').with({ visibilityCheck: true})

fixture('MoOrganisationUnitTree')
  .before(setup)
  .beforeEach(reset)
  .after(teardown)

for (const [selection, contents] of trees.entries()) {
  test
    .page`${baseURL}/organisation/${selection}`
  (`Load of '${selection}'`, async t => {
    await t
      .wait(500)
      .expect(tree.exists)
      .ok()
      .expect(rootNode.exists)
      .ok(`no tree for ${selection}`)
      .expect(VueSelector('mo-tree-view').exists)
      .ok()
      .expect(selected.exists)
      .eql(selection.length > 0, { timeout: 1500 })
      .expect(VueSelector('mo-tree-view')
        .getVue(({ computed }) => JSON.stringify(computed.contents)))
      .eql(JSON.stringify(contents))
  })
}

test
  .page`${baseURL}/organisation/`
('Path changes', async t => {
  await t
    .expect(treeNode.exists)
    .ok()
    .expect(rootNode.exists)
    .ok()
    .expect(currentUnitName.exists)
    .notOk()
    .click(rootNode)
    .expect(currentUnitName.innerText)
    .eql('Hjørring Kommune')
    .expect(rootNode.find('.tree-children').exists)
    .notOk()
    .click(rootNode.find('.tree-arrow'))
    .expect(rootNode.find('.tree-children').exists)
    .ok()

    .click(treeAnchor.withText('Social og sundhed'))
    .expect(currentUnitName.innerText)
    .eql('Social og sundhed')
    .expect(t.eval(() => location.pathname))
    .eql('/organisation/a6773531-6c0a-4c7b-b0e2-77992412b610')
})
