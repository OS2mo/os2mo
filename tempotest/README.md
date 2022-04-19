<!--
SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
SPDX-License-Identifier: MPL-2.0
-->

# OS2mo Tempotest

## Usage
The primary usage of this tool is to test the performance of the OS2mo stack.
```bash
cd tempotest/
docker run --rm -it \
  --volume="$PWD":/tempotest \
  --network=os2mo_default \
  -e MO_URL=http://mo \
  -e AUTH_SERVER=http://keycloak:8080/auth \
  -e CLIENT_SECRET=603f1c82-d012-4d04-9382-dbe659c533fb \
  grafana/k6:latest run /tempotest/script.js --vus=1 --iterations=10
```
To debug, add the `--http-debug=full` flag -- preferably with
`--vus=1 --iterations=1` to avoid (too much) spam. Use `--out=csv=-` to get
_very_ detailed output information, perhaps viewed with `column -s, -t <
file.csv | less -#10 -N -S`.
