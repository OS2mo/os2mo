# Cloud

## Forudsætninger for drift af MO i Azure

### VPN-enhed

Af sikkerhedshensyn kræver OS2mo-cloud-løsningen at al kommunikation mellem jeres
netværk og OS2mo foregår gennem en site-to-site VPN-tunnel. Typisk vil en eksisterende
firewall eller router kunne benyttes, men det er også muligt at benytte en dedikeret enhed.

VPN-enheden skal have en fast offentlig IPv4-adresse, som I oplyser til Magenta for at
forbindelsen kan etableres.

Magenta benytter Azure VPN Gateway, som understøtter enheder med support for IPSEC og
IKE v2 og Routebased. Understøttede enheder inkluderer blandt andet:

- Cisco ASA og ASR
- Juniper SRX
- Check Point Security Gateway
- Fortigate
- pfSense

Specifik opsætning vedrørende VPN-endpoints og netværksopsætning koordineres i detaljer med
Magenta.

### Routing

Når der er etableret en tunnel via VPN-enheden skal der oprettes routes fra jeres serveres IP-
netværk til Microsoft Azure-netværket, sådan at trafik hertil routes igennem VPN-enheden. Det
sker muligvis automatisk under opsætningen af VPN-enheden, afhængigt af hvilken type der
benyttes.

### Firewall-opsætning

Det skal være muligt at tillade udgående trafik til OS2mo-serverne gennem VPN-tunnellen.
Såfremt der benyttes integrationer med on-premises services, såsom Active Directory, skal
indgående trafik til disse kunne tillades. Protokoller der skal kunne kommunikere er:

- LDAP
- SSH
- HTTPS

## Sikkerhed

### Netværkskommunikation

Forbindelsen mellem OS2mo cloud-applikationen og on-premises services skabes via et IPsec-
baseret site-to-site virtuelt privat netværk (VPN). Dvs. at trafikken mellem OS2mo og
eksempelvis Active Directory foregår via det offentlige internet, men i en krypteret tunnel der
kun er adgang til via lukkede netværk på begge sider. Alle pakker sendes således som
krypterede data mellem de to netværk.

Adgangen fra cloud-netværket til on-premises netværket begrænses desuden via firewalls,
sådan at kun specifikke OS2mo applikationsservere kan kommunikere med de interne services.

Magenta koordinerer opsætning af adgangsbegrænsningerne på begge sider af tunellen.

### Datasikkerhed

Data i OS2mo-systemet forlader aldrig de virtuelle private netværk i Microsoft Azure sikrede
datacentre. Databaser kan udelukkende tilgås fra det lukkede og kundespecifikke cloud-
netværk, og der benyttes traditionel adgangskontrol fra applikationerne. Adgang til data i block
storage er begrænset til applikationsservere hvorfra det benyttes.

### Magentas adgang

Opsætning og styring af cloud-systemet foregår via hhv. Microsoft Azure API’er samt en web
baseret konsol. Adgangen til disse begrænses efter princippet om “least privilege” - dvs. kun
medarbejdere hos Magenta som skal kunne styre systemet og administrere infrastrukturen har
adgang. Derudover kræves adgang brug af multi-faktor autentificering ved de pågældende
medarbejderes login i Azure-systemerne.

Når Magentas medarbejdere har behov for at tilgå OS2mo-applikationsserver sker det på en
separat VPN-forbindelse, via en server som er placeret i det lukkede cloud-netværk. Her
begrænses adgangen med firewalls sådan at medarbejderne kun kan tilgå de nødvendige
services, og eksempelvis ikke kan kommunikere med servere i on-premises netværket.

### Compliance

#### Brug af cloud underleverandør

Leverandøren har Kundens generelle godkendelse til at anvende underleverandører til at være
vært for Service og tilhørende data. Hvis der anvendes underleverandører, skal leverandøren
sikre, at en lovlig overførselsgrundlag eksisterer til enhver tid. Ved underskrivelse af Vilkårene
har Leverandøren specificeret brugen af ​​følgende cloud service leverandør:

```{.text}
Microsoft Corporation

One Microsoft Way, Redmond, WA 98052, USA

Overførselsgrundlag: EU -Kommissionens standardkontrakt klausuler og
certificering under EU-U.S. Privacy Shield Framework
```

Leverandøren indgår en skriftlig databehandleraftale med enhver underleverandør, i som
underleverandøren skal være underlagt mindst de samme forpligtelser som Leverandøren har
accepteret i denne databehandlingsaftale med kunden. På ved indgåelse af
databehandlingsaftalen har kunden godkendt, at Microsoft er bruges som en underleverandør.
Denne godkendelse omfatter de vilkår, som leverandøren har accepteret som en del af
abonnementet på Microsoft Azure. Microsoft's databehandling den til enhver tid gældende
aftale findes på www.microsoft.com under "Online Services Data Protection Addendum (DPA)".

Kunden har ret til at få en kopi af leverandørens kontrakt med underleverandør i forbindelse
med bestemmelserne i denne aftale vedrørende databeskyttelse forpligtelser. Leverandøren
underretter Kunden med en skriftlig meddelelse herom måned, når der er ændringer eller
tilføjelser til listen over underleverandører. Hvis kunden har rimelige og specifikke grunde til
ikke at kunne acceptere Leverandørens brug af en ny underleverandør, har kunden ret til at
opsige aftalen uden varsel.

#### Overførsel til tredje land

Overførsel af personoplysninger til tredje land (lande uden for Den Europæiske Union ("EU") og
Det Europæiske Økonomiske Samarbejdsområde ("EØS")) må kun udføres i overensstemmelse
med Kundens instruktioner. Kunden skal løbende opbevares tilstrækkeligt kendskab til det til
enhver tid gældende retsgrundlag for overførsel af personoplysninger uden for EU/EØS. Ved
accept af denne databehandlingsaftale har leverandøren angivet, at Leverandøren gør brug af
databehandlerne uden for EØS, der er anført i afsnit 5 over. Den dataansvarlige har godkendt, at
denne brug af underleverandør er omfattet af instruktion.

#### Dokumentation og overvågning

Efter kundens anmodning skal leverandøren levere alle nødvendige oplysninger til Kunden gør
det muligt for kunden at kontrollere overholdelse af leverandørens forpligtelser i henhold til
denne databehandlingsaftale. Leverandøren skal give adgang til det fysiske leverandørens
faciliteter og bidrager til revisioner, herunder inspektioner, udført af Kunden eller af Kundens
revisor eller anden ekstern rådgiver pålagt af Kunden. Desuden skal Leverandøren give alle
nødvendige oplysninger i forbindelse med dataene behandlingsopgave over for de offentlige
myndigheder, kunden og kundens eksterne rådgivere, i det omfang oplysningerne er
nødvendige for deres opgaver. Leverandøren kan ved skriftlig aftale fakturere Kunden med
rimeligt vederlag for sådanne hjælp. Leverandøren er forpligtet til at føre tilsyn med sine
underleverandører på samme vilkår som Kundens tilsyn med leverandøren. Leverandøren er
forpligtet til at stille til rådighed for kunden evt dokumentation for at påvise, at
leverandøren overholder sin tilsynsforpligtelse.

## Teknik, opsætning og sammenhæng

### Drift af OS2mo-services

OS2mo-services og komponenter til integration afvikles fra virtuelle maskiner på Microsoft
Azure via tre cluster igennem Azure Kubernetes Service (AKS). Deployment vil også foregå
med Terraform og Flux CD.

### Databaser

Der benyttes en managed PostgreSQL database (Azure Database for PostgreSQL flexible
server) til mox/lora-databasen ([1] på diagrammet) med automatiske backups.

I de nuværende opsætninger afvikles databasen i en container med et custom PostgreSQL
image. Derudover kan fordelene ved en managed database udnyttes - herunder automatisk
backup og vedligeholdelse.

### Netværk og VPN

De enkelte kunders systemer - dvs. applikationsservere og databaser - afvikles i segmenterede
netværk i Azure, hvor hver kunde har deres eget VPC, eller et subnet inden for et delt VPC.

Azure VPN Gateway anvendes til at lave en sikker forbindelse mellem kundens netværk og
VPC/subnet i Azure [2]. Forbindelsen fungerer med devices og services som supporterer IPsec
og IKE version 1 og 2.

Kunderne skal således sætte en firewall/gateway op, som opretholder en konstant forbindelse
til netværket i Azure [3]. I nogle tilfælde vil kunderne potentielt have en enhed i forvejen, som er
understøttet og kan anvendes, men det er ikke nødvendigvis tilfældet.

### Server til AD-integration

OS2mo-integrationen til Active Directory kræver adgang til kundens domæne server. Denne
forbindelse sættes op sammen med kunden.

Magenta leverer generelle, overordnede instruktioner til opsætning af denne.

### Miljøer

I de nuværende opsætninger kører der tre miljøer: dev, test og prod. Som udgangspunkt vil hver
kunde få det antal instanser/servere som installationen kræver.

### Magentas adgang til systemerne

Der laves et såkaldt “road warrior” VPN setup, hvor hver udvikler forbinder direkte til en VPN-
server som er placeret i kundens VPC-subnet. Det vil være muligt at forbinde til alle kunders
miljø med samme klientsoftware, men dog med forskellige profiler for hver kunde.

OpenVPN fungerer godt til formålet. Alternativt kan Wireguard, eller Pritunl eksempelvis anvendes.

### Sikkerhed

Løsningen er baseret på at alle netværksservices indkapsles i et virtuelt privat netværk for
dermed at kunne kommunikere direkte med hinanden uden yderligere authentication eller
authorization. Der er således tale om et traditionelt perimeter-baseret “netværksforsvar”,
svarende til når en kunde f.eks. afvikler løsningen i eget datacenter.

Forskellen er at netværkskommunikationen, i denne løsning, sendes krypteret via det offentlige
Internet. Til forskel fra internt på et privat netværk i eget datacenter, hvor trafikken aldrig
rammer Internettet. Dvs. at de centrale fokuspunkter ift. sikkerhed er VPC og VPN-
endepunkterne:

- VPC-netværket som Azure ExpressRoute tilkobles. Segmenteres med et netværk per kunde.
- VPN endpoint. Konfigureres til den enkelte kundes lokale gateway, med en specifik IP og shared secret som opbevares krypteret.
- “Road warrior” VPN til Magentas adgang. Adgangskontrol med to-faktor login.
