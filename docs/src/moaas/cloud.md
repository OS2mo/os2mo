# Cloud

# SaaS (Hetzner)

Magenta tilbyder MO som en fuldt driftet SaaS-løsning på Magentas egen platform hos Hetzner. Al drift, lagring og backup foregår udelukkende i Hetzners datacentre i EU.

## Digital suverænitet

Magenta benytter ikke amerikanske cloud-udbydere til drift af MO. Jeres data opbevares og behandles alene i EU af en europæisk leverandør og er dermed ikke underlagt amerikansk lovgivning som fx CLOUD Act.

## Compliance

- Underleverandør til hosting: Hetzner Online GmbH, Tyskland
- Data opbevares og behandles udelukkende i EU
- Der sker ingen overførsel af personoplysninger til tredjelande
- Magenta er certificeret efter ISO/IEC 27001 og ISO/IEC 27701

De bindende vilkår fremgår af databehandleraftalen mellem jer og Magenta.

## Hvad Magenta varetager

- Hosting og drift af MO og tilhørende integrationer
- Løbende opdateringer og sikkerhedsrettelser
- Backup og overvågning

Hver kunde får tre miljøer: dev, test og prod.

## Sikkerhed

Hver kundes løsning kører i et separat, segmenteret netværk. Forbindelsen mellem MO og jeres lokale systemer (fx Active Directory) er krypteret, og adgangen er begrænset til de nødvendige services. Magentas medarbejdere tilgår systemerne efter princippet om least privilege og med multifaktorautentificering.

Den konkrete opsætning af forbindelsen til jeres netværk aftales i forbindelse med implementeringen.

## Login

Brugerne logger ind via Keycloak, som kobles til jeres egen identitetsudbyder (fx ADFS via SAML). Se [Authentication](../tech-docs/iam/auth.html).

## Alternativ: On-prem

Ønsker I selv at stå for infrastrukturen, kan MO i stedet installeres på jeres egne VM'er. Se [On-prem VM](on-prem.html).