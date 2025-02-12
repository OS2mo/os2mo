# On-prem VM

Ved hosting af MO on-premises udrulles systemet ved hjælp af
konfigurationsstyringssystemet [SALT](https://saltproject.io/). Via SALT
konfigureres hele systemet således, at der ikke er behov for yderligere
vedligeholdelse af de virtuelle maskiner efter adgang er opnået. Dette omfatter
automatisk sikkerhedsopdatering, containerorkestrering, databaseadministration,
køsystem, overvågning, hjælpeværktøjer, konfiguration og selve MO-platformen.

![Overblik over en MO deployment. Der ses en VM på et kundenetværk med MO
installeret på. VM'en forbinder til Magentas SaltStack. Der er også en
reverse-proxy som kan forny certifikater vha. DNS
opsætningen.](../graphics/drift-diagram.svg)

## Tilvejebringelse af servermiljø

Der er behov for tre servere så leverandør og kunde har hver deres testmiljø (hhv. dev og test):

1.  Udviklingsserver
2.  Testserver
3.  Produktionsserver

Bestykning og opsætning skal se sådan ud:

- 8 cores, 16GB Ram og 250 GB SSD harddisk.
- Ubuntu 20.04 eller 22.04.
- Tillad indgående trafik på TCP portene 22, 80, 443.
- Tillad udgående trafik på TCP portene 443, 4505 og 4506.
- Send den anvendte eksterne IP-adresse til Magenta, så der kan åbnes for adgang.
- DNS per miljø jf. [DNS / HTTPS](#dns-https).

Vi vil kraftigt anbefale at Magenta hoster OS2mo.

## Adgange til servermiljø

- VPN-forbindelse tilvejebringes, helst ssh.
- GUI-adgang tilvejebringes.
- Adgang for IdM-brokeren Keycloak tilvejebringes.
- ssh-adgang oprettes til den indledende SALT opkobling.

## Indgåelse af aftaler

- Samarbejdsaftale om krav til fortrolighed og sikkerhed (tavsheds/fortrolighedserklæring)
- Evt. databehandleraftale
- Drifts- og SLA-aftale - forudsætter [etablering af overvågning](#etablering-af-overvagning).

## DNS / HTTPS

Vi vil gerne udstille OS2mo brugergrænsefladen via HTTPS inden for kundens
netværk. Da vi er på et lukket netværk, skal vi bruge DNS records for at
udstede certifikater automatisk. Det kræver 2 DNS records _per server_. Hvis vi
f.eks. have HTTPS på os2mo-udvikling.kunde.dk, kræver det følgende DNS records:

`os2mo-udvikling.kunde.dk CNAME os2mo-udvikling.kunde.dk.os2mo-on-prem.magentahosted.dk`

`_acme-challenge.os2mo-udvikling.kunde.dk CNAME _acme-challenge.os2mo-udvikling.kunde.dk.os2mo-on-prem.magentahosted.dk`

## Etablering af overvågning

Overvågning er en forudsætning for sikring af oppetid og rettidig indgriben ved
uhensigtsmæssigheder og fejl. Overvågning gør det ligeledes muligt at generere
SLA-rapporter med beregnede oppe- og svartider.
