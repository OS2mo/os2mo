---
title: Best practices for implementering
---

## Projektopstart
### Tilvejebringelse af servermiljø
**Ansvarlig/udførende:** Kunde

Der er behov for fire servere:                                     
                                                                   
1.  Udviklingsserver                                               
2.  Testserver                                                     
3.  Produktionsserver                                              
4.  Applikationsovervågningsserver                                 
                                                                   
Det er muligt at installere oven på myndighedens eget container-miljø (VMware el.lign.). 
                                                     
Servere:                                                           
                                                                   
-   Produktions-VM bestykket med 4 cores, 8GB Ram og 60 GB SSD     
    harddisk                                                       
-   Andre VM'er (udvikling og test): 2 cores, 4GB Ram og 30 GB SSD 
    harddisk                                                       
-   Ubuntu 16.04                                                   
-   Tillade indgående trafik på portene 22, 80, 443                
-   Tillade udgående trafik på portene 4505 og 4506 (Saltstack)    
-   Send den anvendte eksterne IP-adresse til Magenta, så der kan  
    åbnes for adgang.

### Adgange til servermiljø
**Ansvarlig/udførende:** Kunde

- VPN-forbindelse tilvejebringes
- Én administratorkonto oprettes til den indledende opkobling til vores deploymentmiljø for distribueret management.
- Deploymentserverens IP-adresse er 178.23.177.238, og dens værtsnavn er ctrl1.magenta.dk.

### Indgåelse af aftaler 
**Ansvarlig/udførende:** Kunde

- Samarbejdsaftale om krav til fortrolighed og sikkerhed (tavsheds/fortrolighedserklæring)
- Evt. databehandleraftale
- Drifts- og SLA-aftale

### Tilvejebringelse af SSL certifikater
**Ansvarlig/udførende:** Kunde

Vi vil gerne udstille OS2mo brugergrænsefladen via HTTPS inden for kommunens netværk. Dertil skal vi bruge SSL-certifikater. Se [SSL-certifikatvejledning](../static/SSL-certifikat%20vejledning.pdf)

## Installation af OS2mo
### OS2mo installeres på de tilvejebragte servere
**Ansvarlig/udførende:** Leverandør

Installationen sikrer at kunden har OS2mo til rådighed med et sæt test-data, der i størrelse ligner kundens egen organisation

### OS2mo servere indbindes evt i Windows-domæne
**Ansvarlig/udførende:** Kunde

Viborg har tilføjet OS2MO-serveren til deres Windows-domæne og har i den forbindelse lavet en guide, der beskriver:

- Tilføjelse af OS2MO server til Windows domænet
- Powershell remote server opsætning
- Skjult CPR-nummer i AD

Se [AD - OS2MO opsætnings guide](../static/AD%20-%20OS2MO%20opsætnings%20guide.pdf).

## Integration med Dansk Adresse Register (DAR)
**Ansvarlig/udførende:** Leverandør

OS2MOs addresseopslag konfigureres til at foretrække adresser inden for kommunen.

## Integration med SAML SSO 2.0
**Ansvarlig/udførende:** Kunde / Leverandør

Opgaven forudsætter, at Kunden har en IdP, der understøtter SAML 2.0 SSO. Simpel rollestyring (rettigheder til at skrive alt, eller så har man ingen rettigheder) styres via oprettelse af en bruger i AD’et. Se OS2MO ADFS Mini Guide.

- OS2MO 2.0 skal oprettes som en SP (Service Provider) hos IdP’en. OS2MO 2.0 udstiller metadata i XML-format, når løsningen er udrullet, så kunden får en URL til et metadata endpoint, som de kan give til IdP’en. Derefter sker konfigurationen automatisk
- Kunden sender en URL til IdP’ens metadata for SAML SSO
- Brugerens navn, og eventuelle roller skal i IdP’en tilføjes til de claims, der kommer tilbage i SAML-token

Hvis det er påkrævet at forespørgsler er signerede, kræves et sæt certifikater (public certificate og private key).

## Integration med Serviceplatformen
### OS2MO som anvendersystem på Serviceplatformen
**Ansvarlig/udførende:** Kunde

Der skal laves en aftale til at aktivere de to agenter og slå personer op i Serviceplatformens CPR-service samt til hændelsesdata, så personoplysninger forbliver ajourførte i OS2MO. Se [vejledning til tilslutning af OS2MO på Serviceplatformen som anvendersystem](../static/Vejledning%20til%20tilslutning%20af%20OS2MO%20på%20Serviceplatformen%20som%20anvendersystem.pdf).

- Send de respektive FOCES inkl. keystore password, samt de 4 UUID’er fra serviceaftalen til leverandøren

### OS2MO som anvendersystem på Støttesystemet Organisation
**Ansvarlig/udførende:** Kunde

OS2MO kan opdatere Støttesystemet Organisation igennem OS2-komponenten OS2Sync (tidl. StsOrgSync). Her kræves serviceaftale, oprettet IT-system og FOCES. Se [vejledning til opsætning af STSOrgSync med OS2MO](../static/Vejledning%20til%20STSOrgSync%20v3.pdf).

- Send de respektive FOCES inkl. keystore password, samt de 4 UUID’er fra serviceaftalen til leverandøren

## Indlæsning af organisationsdata
### Tilvejebringelse af data
**Ansvarlig/udførende:** Kunde

Kunden tilvejebringer data med kundens organisations- og medarbejderdata efter aftale om datakilde og format. Data kommer sædvanligvis fra lønsystemet.

Hvis organisations- og medarbejderdata kommer fra SD-løn må oplysninger om ledere fremskaffes på anden vis, for eksempel via regneark.

### Indlæsning af data i OS2mo
**Ansvarlig/udførende:** Leverandør

Leverandøren indlæser data i OS2mo.

## Integration med Lønsystem
### Integration med KMD OPUS
**Ansvarlig/udførende:** Kunde / Leverandør

Konfiguration og eventuel tilpasning af komponent udviklet i OS2-regi.

Integration med OPUS forgår typisk via XML-dump fra KMD, som hver nat placeret på KFS LAN.

For at OS2mo skal kunne opdateres hver nat, skal følgende ske - se afsnittet Opsætning: https://os2mo-data-import-and-export.readthedocs.io/en/latest/main.html#id4

### Integration med Silkeborgdata SD-Løn
**Ansvarlig/udførende:** Leverandør

Konfiguration og eventuel tilpasning af komponent udviklet i OS2-regi.

Integration med SD-løn kræver adgang via oplysning om:

- Institution Identifer
- Brugernavn
- Password

## Integration med Active Directory
**Ansvarlig/udførende:** Kunde

Konfiguration og eventuel tilpasning af komponent udviklet i OS2-regi.

Integrationen overfører data fra AD til OS2mo, se afsnittet Opsætning: https://os2mo-data-import-and-export.readthedocs.io/en/latest/main.html#integration-til-active-directory

## Integration med OS2rollekatalog
**Ansvarlig/udførende:** Leverandør

Konfiguration og eventuel tilpasning af komponent udviklet i OS2-regi.

Integrationen overfører data fra OS2mo til OS2rollekatalog ved natlige kørsler.

## Integration med Telefonbogen
**Ansvarlig/udførende:** Leverandør

Konfiguration og eventuel tilpasning af komponent udviklet i OS2-regi.

Data fra OS2mo kan sendes til en telefonbog, som medarbejdere kan tilgå via intranet.