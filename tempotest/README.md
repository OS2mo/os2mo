<!--
SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
SPDX-License-Identifier: MPL-2.0
-->

# OS2mo Tempotest

## Usage
The primary usage of this tool is to test the performance of the OS2mo stack.
```bash
docker build . -t os2mo-tempotest
docker run --rm -it \
       --network=os2mo_default \
       -e MO_URL=http://mo \
       -e AUTH_SERVER=http://keycloak:8080/auth \
       -e CLIENT_SECRET=603f1c82-d012-4d04-9382-dbe659c533fb \
       os2mo-tempotest --vus=1 --iterations=10
```
To debug, add the `--http-debug=full` flag -- preferably with `--vus=1 --iterations=1` to avoid (too much) spam. Use
`--out=csv` to get _very_ detailed output information, perhaps viewed with `column -s, -t < file.csv | less -#10 -N -S`.


## Deployment
https://k6.io/docs/results-visualization/prometheus/
```
K6_PROMETHEUS_REMOTE_URL = http://localhost:9090/api/v1/write
K6_PROMETHEUS_USER
K6_PROMETHEUS_PASSWORD
K6_KEEP_NAME_TAG = true
K6_OUT=output-prometheus-remote
```
To enable remote write in Prometheus 2.x use --enable-feature=remote-write-receiver option. See docker-compose samples in example/. Options for remote write storage can be found here.
TODO #48631
