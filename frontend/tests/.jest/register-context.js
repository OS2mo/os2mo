// SPDX-FileCopyrightText: 2017-2021 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

// This file helps mock `require.context` when running the Vue unit tests.
// See:
// https://github.com/storybookjs/storybook/tree/master/addons/storyshots/storyshots-core#option-1-plugin
// for more details.

import registerRequireContextHook from "babel-plugin-require-context-hook/register"
registerRequireContextHook()
