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
   * - 2.
     - Adgange til servermiljø
     -
       * VPN-forbindelse tilvejebringes

       * Én administratorkonto oprettes til den indledende opkobling til vores deploymentmiljø for distribueret management.

       * Deploymentserverens IP-adresse er ``178.23.177.238``, og dens værtsnavn er ``ctrl1.magenta.dk``.
     - Kunde
   * - 3.
     - Indgåelse af aftaler
     -
       * Databehandleraftale.

       * Fortrolighedsaftale, om nødvendigt.
     - Kunde
   * -
     -
     -
       * Kontrakt
     - Leverandør
   * - 4.
     - Tilvejebringelse af SSL certifikater
     - OS2MO 2.0 skal udstilles på Kundens interne netværk (skyen eller lokalt) via HTTPS.
     - Kunde
   * - 5.
     - Tilvejebringelse af certifikater til Serviceplatformen
     - Der skal laves en aftale til at aktivere de to agenter og slå personer op i Serviceplatformens CPR-service samt til hændelsesdata, så personoplysninger forbliver ajourførte i OS2MO.
       Se `vejledning til tilslutning af OS2MO på Serviceplatformen som anvendersystem <vejledning1_>`_.

       .. _vejledning1: _static/Vejledning%20til%20tilslutning%20af%20OS2MO%20p%C3%A5%20Serviceplatformen%20som%20anvendersystem.pdf

       * Send de respektive FOCES inkl. keystore password, samt de 4 UUID'erne fra serviceaftalen til leverandøren
     - Kunde
   * - 6.
     - Installation af OS2MO og tilhørende agenter
     - Se de enkelte trin nedenfor.
     - Leverandør
   * - 6. 1
     - Agent til autentificering (SAML 2.0 SSO)
     - Simpel rollestyring (rettigheder til at skrive alt, eller så har man ingen rettigheder) styres via oprettelse af en bruger i AD'et.
       Se `OS2MO ADFS Mini Guide <vejledning2_>`_.

       .. _vejledning2: _static/OS2MO\ ADFS\ Mini\ Guide.pdf

       * OS2MO 2.0 skal oprettes som en SP (Service Provider) hos IdP'en. OS2MO 2.0 udstiller metadata i XML-format, når løsningen er udrullet, så kunden får en URL til et metadata endpoint, som de kan give til IdP'en. Derefter sker konfigurationen automatisk

       * Kunden sender en URL til IdP'ens metadata for SAML SSO

       * Brugerens navn, og eventuelle roller skal i IdP'en tilføjes til de claims, der kommer tilbage i SAML-token

       Hvis det er påkrævet at forespørgsler er signerede, kræves et sæt certifikater (public certificate og private key)

       Opgaven forudsætter, at Kunden har en IdP, der understøtter SAML 2.0 SSO.
     - Kunde / Leverandør
   * - 6. 2
     - Agent til Dansk Adresse Register (DAR)
     - Implementeringen foregår normalt automatisk, men en konfiguration i OS2MO 2.0 skal informere brugergrænsefladen om, at den nu befinder sig i given kommune og skal slå adresser op inden for kommunegrænsen
     - Leverandør
   * - 6. 3
     - Agent til Serviceplatformens CPR-data
     - Se også ID 5
       Der er behov for to services:
       1.Opslag på Serviceplatformen ved ansættelse af en medarbejder (LaesPerson)
       2.Løbende synkronisering mellem databasen (LoRa) og Serviceplatformens CPR-service (LaesPersonAendringer)
     - Leverandør
   * - 7.
     - Data i OS2MO
     - OS2MO populeres med Kundens organisaions- og medarbejderdata.
       Se de enkelte trin nedenfor.
     - Kunde / Leverandør
   * - 7. 1
     - Tilvejebringelse af data
     - Kunden tilvejebringer adgang til API eller et databasedump med myndighedens organisations- og medarbejderdata
     - Kunde
   * - 7. 2
     - Indlæsning af data
     - Leverandøren mapper data til OIO-standarden og indlæser dem i OS2MO’s database, LoRa
     - Leverandør
   * - 8.
     - Integration med øvrig infrastruktur
     - Kommuner binder OS2MO sammen med øvrig infrastruktur på både system- og dataniveau 
       Se eksempler og guides nedenfor
     - Kunde / Leverandør
   * - 8. 1
     - OS2MO i et Windows Domæneme
     - Viborg har tilføjet OS2MO-serveren til deres Windows-domæne og har i den forbindelse lavet en guide, der beskriver:

       * Tilføjelse af OS2MO server til Windows domænet

       * Powershell remote server opsætning

       * Skjult CPR-nummer i AD

       Se `AD - OS2MO opsætnings guide <vejledning3_>`_.   

       .. _vejledning3: _static/AD\ -\ OS2MO\ opsætnings\ guide.pdf 

     - Kunde
