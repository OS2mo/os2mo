Release type: major

[#52131] Expose the `file_storage` setting to the frontend

[#52131] Change the default `file_storage` backend from `filesystem` to `noop`.
This disables file upload on all servers without a overwrite. This was
overwritten for all salt deployment in
[MR2494](https://git.magenta.dk/labs/salt-automation/-/merge_requests/2494).
