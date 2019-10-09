
.. _cookbook:

Best practices for implementering
=================================

.. raw:: html

   <style>
   table.table-100{
       width: 100% !important
   }
   table.table-100 * {
       white-space: normal !important;
       vertical-align: top !important;
       font-size: 95% !important;
   }
   </style>

.. list-table:: Beskrivelse af implementeringsfaserne ved installation af OS2MO 2.0
   :header-rows: 1
   :widths: 1 1 100 1
   :class: table-100

   * - ID
     - Opgave
     - Beskrivelse
     - Ansvarlig/ udførende
   * - 1.
     - Projektopstart
     - 
     -
   * - 1. 1
     - Tilvejebringelse af servermiljø
     - Der er behov for fire servere:

       1. Udviklingsserver
       2. Testserver
       3. Produktionsserver
       4. Applikationsovervågningsserver

       Det er muligt at installere oven på myndighedens eget container-miljø (VMware el.lign.).

       Servere:

       * Produktions-VM bestykket med 4 cores, 8GB Ram og 60 GB SSD harddisk
       * Andre VM’er (udvikling og test): 2 cores, 4GB Ram og 30 GB SSD harddisk
       * Ubuntu 16.04
       * Tillade udgående trafik på portene 22, 80, 443, 4505 og 4506
       * Send den anvendte eksterne IP-adresse til Magenta, så der kan åbnes for adgang.
     - Kunde
   * - 1. 2
     - Adgange til servermiljø
     -
       * VPN-forbindelse tilvejebringes

       * Én administratorkonto oprettes til den indledende opkobling til vores deploymentmiljø for distribueret management.

       * Deploymentserverens IP-adresse er ``178.23.177.238``, og dens værtsnavn er ``ctrl1.magenta.dk``.
     - Kunde
   * - 1. 3
     - Indgåelse af aftaler
     -
       * Samarbejdsaftale om krav til fortrolighed og sikkerhed (tavsheds/fortrolighedserklæring)
       * Evt. databehandleraftale
       * Drifts- og SLA-aftale
     - Kunde
   * - 1. 4
     - Tilvejebringelse af SSL certifikater
     - Vi vil gerne udstille OS2mo brugergrænsefladen via HTTPS inden for kommunens netværk. Dertil skal vi bruge SSL-certifikater
     - Kunde
   * - 2.
     - Installation af OS2mo
     -
     -
   * - 2. 1
     - OS2mo installeres på de tilvejebragte servere.
     - Installationen sikrer at kunden har OS2mo til rådighed med et sæt test-data, der i størrelse ligner kundens egen organisation
     - Leverandør
   * - 2. 2
     - OS2mo servere indbindes evt i Windows-domæne
     - Viborg har tilføjet OS2MO-serveren til deres Windows-domæne og har i den forbindelse lavet en guide, der beskriver:

       * Tilføjelse af OS2MO server til Windows domænet
       * Powershell remote server opsætning
       * Skjult CPR-nummer i AD
       Se `AD - OS2MO opsætnings guide <vejledning3_>`_.   

       .. _vejledning3: _static/AD\ -\ OS2MO\ opsætnings\ guide.pdf 

     - Kunde
   * - 3.
     - Integration med Dansk Adresse Register (DAR)
     - OS2MOs addresseopslag konfigureres til at foretrække adresser inden for kommunen
     - Leverandør
   * - 4.
     - Integration med SAML SSO 2.0 
     - Opgaven forudsætter, at Kunden har en IdP, der understøtter SAML 2.0 SSO.
       Simpel rollestyring (rettigheder til at skrive alt, eller så har man ingen rettigheder) styres via oprettelse af en bruger i AD'et.
       Se `OS2MO ADFS Mini Guide <vejledning2_>`_.

       .. _vejledning2: _static/OS2MO\ ADFS\ Mini\ Guide.pdf
       * OS2MO 2.0 skal oprettes som en SP (Service Provider) hos IdP'en. OS2MO 2.0 udstiller metadata 
	 i XML-format, når løsningen er udrullet, så kunden får en URL til et metadata endpoint, 
	 som de kan give til IdP'en. Derefter sker konfigurationen automatisk
       * Kunden sender en URL til IdP'ens metadata for SAML SSO
       * Brugerens navn, og eventuelle roller skal i IdP'en tilføjes til de claims, der kommer tilbage i SAML-token

       Hvis det er påkrævet at forespørgsler er signerede, kræves et sæt certifikater (public certificate og private key)
     - Kunde / Leverandør
   * - 5.
     - Integration med Serviceplatformen
     -
     -
   * - 5. 1
     - OS2mo som anvendersystem på Serviceplatformen
     - Der skal laves en aftale til at aktivere integration med og opslag i Serviceplatformens CPR-service samt evt til hændelsesdata, hvis personoplysninger skal ajourføres i OS2MO.
       Se `vejledning til tilslutning af OS2MO på Serviceplatformen som anvendersystem <vejledning5_1_>`_.

       .. _vejledning5_1: _static/Vejledning%20til%20tilslutning%20af%20OS2MO%20p%C3%A5%20Serviceplatformen%20som%20anvendersystem.pdf

       Kunde overdrager de respektive FOCES inkl. keystore password, samt de 4 UUID'er fra serviceaftalen til leverandøren
     - Kunde
   * - 6.
     - Indlæsning af organisationsdata
     -
     -
   * - 6. 1
     - Tilvejebringelse af data 
     - Kunden tilvejebringer data med kundens organisations- og medarbejderdata
       efter aftale om datakilde og format. Data kommer sædvanligvis fra lønsystemet.

       Hvis organisations- og medarbejderdata kommer fra SD-løn må oplysninger om ledere fremskaffes på anden vis, for eksempel via regneark.
     - Kunde
   * - 6. 2
     - Indlæsning af data i OS2mo
     - Leverandøren indlæser data i OS2mo. 
     - Leverandør
   * - 7.
     - Integration med Lønsystem
     - 
     - 
   * - 7. 1
     - Integration med KMD OPUS
     - Konfiguration og eventuel tilpasning af komponent udviklet i OS2-regi.

       Integration med OPUS forgår typisk via XML-dump fra KMD, som hver nat placeret på KFS LAN.

       For at OS2mo skal kunne opdateres hver nat, skal følgende ske - se afsnittet Opsætning: https://os2mo-data-import-and-export.readthedocs.io/en/latest/main.html#id4
     - Kunde / Leverandør
   * - 7. 2
     - Integration med Silkeborgdata SD-Løn
     - Konfiguration og eventuel tilpasning af komponent udviklet i OS2-regi.

       Integration med SD-løn kræver adgang via oplysning om:  

       * Institution Identifer
       * Brugernavn
       * Password
     - Leverandør
   * - 8.
     - Integration med Active Directory
     - Konfiguration og eventuel tilpasning af komponent udviklet i OS2-regi.

       Agenten skriver data fra AD til OS2mo, se afsnittet Opsætning: https://os2mo-data-import-and-export.readthedocs.io/en/latest/main.html#integration-til-active-directory
     - Kunde
   * - 9.
     - Integration med Støttesystemet Organisation
     - OS2mo kan opdatere Støttesystemet Organisation igennem OS2-komponenten OS2Sync (tidl. StsOrgSync). Her kræves serviceaftale, oprettet IT-system og FOCES. 
       Se `vejledning til opsætning af STSOrgSync med OS2mo <vejledning5_2_>`_.

       .. _vejledning5_2: _static/Vejledning%20til%20STSOrgSync%20v3.pdf

       Kunde overdrager de respektive FOCES inkl. keystore password, samt de 4 UUID'er fra serviceaftalen til leverandøren
     - Kunde
   * - 10.
     - Integration med OS2rollekatalog
     - Konfiguration og eventuel tilpasning af komponent udviklet i OS2-regi.

       Agenten skal skrive data fra OS2mo til OS2rollekatalog ved natlige kørsler
     - Leverandør
   * - 11.
     - Integration med Telefonbogen
     - Konfiguration og eventuel tilpasning af komponent udviklet i OS2-regi.

       Data fra OS2mo kan sendes til en telefonbog, som medarbejdere kan tilgå via intranet.
     - Leverandør

