# On-prem VM

## Tilvejebringelse af servermiljø

Der er behov for tre servere så leverandør og kunde har hver deres testmiljø (hhv. dev og test):

1.  Udviklingsserver
2.  Testserver
3.  Produktionsserver

Bestykning og opsætning skal se sådan ud:

-   4 cores, 16GB Ram og 60 GB SSD harddisk
-   Ubuntu 20.04
-   Tillade indgående trafik på portene 22, 80, 443
-   Tillade udgående trafik på portene 4505 og 4506
-   Send den anvendte eksterne IP-adresse til Magenta, så der kan åbnes for adgang.

Vi vil kraftigt anbefale at Magenta hoster OS2mo.

## Adgange til servermiljø

- VPN-forbindelse tilvejebringes
- Én administratorkonto oprettes til den indledende opkobling til vores deploymentmiljø for distribueret management.

## Indgåelse af aftaler

- Samarbejdsaftale om krav til fortrolighed og sikkerhed (tavsheds/fortrolighedserklæring)
- Evt. databehandleraftale
- Drifts- og SLA-aftale - Forudsætter opsætning af monitorering.

## HTTPS

Vi vil gerne udstille OS2mo brugergrænsefladen via HTTPS inden for kundens
netværk. Da vi er på et lukket netværk, skal vi bruge DNS records for at
udstede certifikater automatisk. Det kræver 2 DNS records _per server_. Hvis vi
f.eks. have HTTPS på os2mo-udvikling.kunde.dk, kræver det følgende DNS records:

`os2mo-udvikling.kunde.dk CNAME os2mo-udvikling.kunde.dk.os2mo-on-prem.magentahosted.dk`

`_acme-challenge.os2mo-udvikling.kunde.dk CNAME _acme-challenge.os2mo-udvikling.kunde.dk.os2mo-on-prem.magentahosted.dk`

## Etablering af overvågning

Overvågning er en forudsætning for sikring af oppetid og rettidig indgriben ved uhensigtsmæssigheder og fejl. Overvågning gør det ligeledes muligt at generere SLA-rapporter med beregnede oppe- og svartider.
