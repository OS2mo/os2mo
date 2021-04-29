// SPDX-FileCopyrightText: 2021- Magenta ApS
// SPDX-License-Identifier: MPL-2.0


export let columns = [

    {label: 'engagement_id', data: 'user_key', field: null},
    {label: 'job_function', data: 'job_function'},
    {label: 'engagement_type', data: 'engagement_type'}
]

export function generate_extension_columns(extension_labels) {
    if (extension_labels.length > 0 && extension_labels[0] !== "") {
        return extension_labels.map((label, index) => ({
            label: label,
            data: 'extension_' + String(index + 1)
        }))
    }
    return [];

}
