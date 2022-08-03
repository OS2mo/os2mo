// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { Selector } from "testcafe"
import VueSelector from "testcafe-vue-selectors"
import { baseURL, setup, teardown } from "./support"
import { login } from "./login"

const trees = new Map([
  ["", ["> Lønorganisation", "> Overordnet Enhed"]],
  [
    "2874e1dc-85e6-4269-823a-e1125484dfd3",
    ["> Lønorganisation", "> =+= Overordnet Enhed =+="],
  ],
  [
    "85715fc7-925d-401b-822d-467eb4b163b6",
    [
      "> Lønorganisation",
      {
        "Overordnet Enhed": [
          {
            "Humanistisk fakultet": ["=+= Filosofisk Institut =+="],
          },
          "Samfundsvidenskabelige fakultet",
          "> Skole og Børn",
          "Social og sundhed",
        ],
      },
    ],
  ],
  [
    "fa2e23c9-860a-4c90-bcc6-2c0721869a25",
    [
      "> Lønorganisation",
      {
        "Overordnet Enhed": [
          "> Humanistisk fakultet",
          "Samfundsvidenskabelige fakultet",
          {
            "Skole og Børn": ["=+= IT-Support =+="],
          },
          "Social og sundhed",
        ],
      },
    ],
  ],
])

let tree = VueSelector("mo-tree-view")
let treeNode = tree.find(".tree-node")
let treeAnchor = treeNode.find(".tree-anchor")
let rootNode = treeNode.withText("Overordnet Enhed")
let selected = treeNode.filter(".selected")

let currentUnitName = Selector(".orgunit .orgunit-name").with({ visibilityCheck: true })

fixture("MoOrganisationUnitTree")
  .before(setup)
  .after(teardown)
  .beforeEach(async (t) => {
    await login(t)
  })

for (const [selection, contents] of trees.entries()) {
  test.page`${baseURL}/organisation/${selection}`(
    `Load of '${selection}'`,
    async (t) => {
      await t
        .wait(5000)
        .expect(tree.exists)
        .ok()
        .expect(rootNode.exists)
        .ok(`no tree for ${selection}`)
        .expect(VueSelector("mo-tree-view").exists)
        .ok()
        .expect(selected.exists)
        .eql(selection.length > 0, { timeout: 3000 })
        .expect(
          VueSelector("mo-tree-view").getVue(({ computed }) =>
            JSON.stringify(computed.contents)
          )
        )
        .eql(JSON.stringify(contents))
    }
  )
}

test.page`${baseURL}/organisation/`("Path changes", async (t) => {
  await t
    .wait(5000)
    .expect(treeNode.exists)
    .ok()
    .expect(rootNode.exists)
    .ok()
    .expect(currentUnitName.exists)
    .notOk()
    .click(rootNode)
    .expect(currentUnitName.innerText)
    .eql("Overordnet Enhed")
    .expect(rootNode.find(".tree-children").exists)
    .notOk()
    .click(rootNode.find(".tree-arrow"))
    .expect(rootNode.find(".tree-children").exists)
    .ok()

    .click(treeAnchor.withText("Social og sundhed"))
    .expect(currentUnitName.innerText)
    .eql("Social og sundhed")
    .expect(t.eval(() => location.pathname))
    .eql("/organisation/68c5d78e-ae26-441f-a143-0103eca8b62a")
})
