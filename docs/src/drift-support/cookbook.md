---
title: Implementeringsguide
---

## Projektopstart
### Tilvejebringelse af servermiljø

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

### Adgange til servermiljø

- VPN-forbindelse tilvejebringes
- Én administratorkonto oprettes til den indledende opkobling til vores deploymentmiljø for distribueret management.

### Indgåelse af aftaler

- Samarbejdsaftale om krav til fortrolighed og sikkerhed (tavsheds/fortrolighedserklæring)
- Evt. databehandleraftale
- Drifts- og SLA-aftale - Forudsætter opsætning af monitorering.

### HTTPS

Vi vil gerne udstille OS2mo brugergrænsefladen via HTTPS inden for kundens
netværk. Da vi er på et lukket netværk, skal vi bruge DNS records for at
udstede certifikater automatisk. Det kræver 2 DNS records _per server_. Hvis vi
f.eks. have HTTPS på os2mo-udvikling.kunde.dk, kræver det følgende DNS records:

`os2mo-udvikling.kunde.dk CNAME os2mo-udvikling.kunde.dk.os2mo-on-prem.magentahosted.dk`

`_acme-challenge.os2mo-udvikling.kunde.dk CNAME _acme-challenge.os2mo-udvikling.kunde.dk.os2mo-on-prem.magentahosted.dk`

### Etablering af overvågning
Overvågning er en forudsætning for sikring af oppetid og rettidig indgriben ved uhensigtsmæssigheder og fejl. Overvågning gør det ligeledes muligt at generere SLA-rapporter med beregnede oppe- og svartider.

## Installation af OS2mo
### OS2mo installeres på de tilvejebragte servere

Installationen sikrer at kunden har de grundliggende komponenter på plads: OS2mo, OIO og den Lokale Rammearkitektur til rådighed.

### OS2mo servere indbindes evt i Windows-domæne ifm. integration til Active Directory

OS2mo integrerer meget ofte med Active Directory for at oplysninger kan blive udvekslet mellem de to systemer.

Der er udarbejdet en guide som beskriver:

- Tilføjelse af OS2mo-servere til Windows domænet
- Powershell remote server-opsætning
- Skjult CPR-nummer i Active Directory

Se [AD - OS2mo opsætningsguide](../static/AD%20-%20OS2MO%20opsætnings%20guide.pdf).

## Integration med Dansk Adresse Register (DAR)

OS2mos addresseopslag konfigureres til fx kun at kunne vælge adresser inden for en kommunes grænser.

## Log på med dit eget logon

Det skal være muligt at logge på OS2mo med sit eksisterende logon.

Opgaven forudsætter at kunden har en IdP der understøtter SAML 2.0 SSO.

[Se hvordan opsætningen skal se ud i ADFS her](https://rammearkitektur.docs.magenta.dk/-/os2mo/-/jobs/510013/artifacts/site/guides/adfs-setup.html).

## Adgangsbaseret rollestyring

Det skal ligeledes være muligt at styre hvem der har adgang til hvad i OS2mo. Rollestyring forvaltes via oprettelse af en bruger i AD’et, opsætning i en IdP (fx ADFS), i [Keycloak](https://www.keycloak.org/) og i OS2mo.

## Integration med Serviceplatformen og FK Org
### OS2mo som anvendersystem på FK Org på Serviceplatformen

OS2mo kan opdatere FK Organisation igennem OS2-komponenten OS2sync.
Se [Vejledning til Serviceplatformen til FK Org](https://drive.google.com/file/d/1w5DnucWrkW2vrK_et-79yA-M6w1G3b6g/view)

OS2mo kan ligeledes hente personoplysninger fra CPR-registret.

Der skal laves en serviceaftale for at kunne benytte hhv. [FK Organisation](https://digitaliseringskataloget.dk/l%C3%B8sninger/organisation) og [CPR-services](https://cpr.dk/kunder/private-virksomheder/cpr-services) på Serviceplatformen.

- Send de to FOCES-certifikater inkl. keystore password til Magenta. Der skal bruges to certifikater - et til FK Organisation TEST og etn til FK Organisation prod)
Bemærk at certifikatet skal være i .p12-format.

+KOMBIT har også udarbejdet [Brugervejledning til Administrationsmodulerne for myndigheder - Sådan bruger du STS Administration og Serviceplatformens Administrationsmodul](https://digitaliseringskataloget.dk/files/integration-files/151120211250/Brugervejledning%20til%20Administrationsmodulerne%20for%20myndigheder.pdf).

## Indlæsning af organisationsdata
### Tilvejebringelse af data

Kunden tilvejebringer organisations- og medarbejderdata. Data kommer sædvanligvis fra lønsystemet (SD-Løn eller OPUS).

Data beriges typisk med data fra Active Directory, Danmarks AdresseRegister og - i nogle tilfælde - fra csv-filer. OS2mo's datagrundlag er kun så godt som de tilvejebragte tillader. Implementering af OS2mo er derfor ofte forbundet med grundig datavask i kildesystemerne til sikring af høj datakvalitet.

### Indlæsning af data i OS2mo

Leverandøren foretager en engangsindlæsning af data i OS2mo. Denne indlæsning muliggør inspektion og test af data. Når datagrundlaget vurderes at være af høj kvalitet, kan integrationerne sættes op så daglig indlæsning automatiseres (se nedenfor)

## Integration med Lønsystem
### Integration med KMD OPUS

Opgaven består i intsallation, konfiguration og eventuel tilpasning af integrationen.

Integrationen med OPUS foregår via XML-dump fra KMD som hver nat placeres på KFS LAN. XML-dumpet skal rekvireres fra KMD.

Samtidigt hermed skal [denne integration Active Directory opsættes](../data-import-export/integrations/ad.md)

### Integration med SD-Løn

Opgaven består i installation, konfiguration og eventuel tilpasning af integrationen.

Integration med SD-løn kræver adgang via oplysning om:

- Institution Identifer
- Brugernavn
- Password

#### SD-Tool

SD-Tool kompenserer for visse begræsninger i SD's API sådan medarbejdere flyttes korrekt til de afdelinger de rent faktisk arbejder i.

#### SD-MOX

SD-MOX gør det muligt at foretage organisationsændringer i OS2mo og skrive dem tilbage til SD-Løn - i stedet for omvendt.

## Integration med Active Directory

Opgaven består i installation, konfiguration og eventuel tilpasning af integrationen.

Opgaven udføres i tre trin:

- AD-sync - Beriger OS2mo's data med AD-data.
- Lille AD-skriv - Skriver OS2mo's UUID'er til et ExtensionAttribute-felt i AD'et til sikring af konsistent bruger-UUID på tværs af systemer.
- Store AD-Skriv - Sørger for at OS2mo's organisation og brugere overføres til Active Directory så OS2mo også bliver autoritativ for Active Directory og brugeroprettelse sker automatisk.

[Se udførlig beskrivelse af AD-integrationen.](../data-import-export/integrations/ad.md)

## Integration med OS2rollekatalog

Opgaven består i installation, konfiguration og eventuel tilpasning af integrationen.

Integrationen leverer OS2mo's datagrundlag til OS2rollekatalog ved natlige kørsler mhp. at tildele roller til medarbejderne i [OS2rollekatalog.](https://os2.eu/produkt/os2rollekatalog)

## Integration med Organisationsdiagrammet

Opgaven består i installation, konfiguration og eventuel tilpasning af integrationen.

Data fra OS2mo sendes til et organisationsdiagram som medarbejdere kan tilgå via intranettet eller internettet. Organisationsdiagrammet lever op til gældende tilgængelighedslovgivning og kan tilgås fra forskellige skærmstørrelser (mobil, tablet, pc).

## Integration med KLE online

Det er muligt at integrere med [KLE Online](http://www.kle-online.dk/soegning) så opmærkning af organisationsenheder kan foretages i OS2mo's brugergrænseflade.

## Udstilling af data til forskellige SQL-databaser

OS2mo kan sende sine data til SQL-databaser.

## Implementering af skræddersyede rapporter

Til Trivselsundersøgelser, MUS-opfølgning, Ledelsesrapportering, mv.
