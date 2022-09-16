---
title: Powershell script til AD-Skriv
---

Nedensor beskrives opsætning og funktionalitet.

## Opsætning

ADStruktur.ps1 skal sættes op med flg. indstillinger:

- $SettingOURoot = "OU=Rod,DC=kommune,DC=dk"
Skal være oprettet i forvejen. Angiver rod-enheden hvor scriptet skal arbejde fra.
- $SettingOUInactiveUsers = "OU=Nye OS2MO brugere,OU=Rod,DC=kommune,DC=dk"
Skal være oprettet i forvejen. Angiver OU'en, hvor ADSkriv opretter inaktive AD-brugere.
- $SettingAutoritativOrg = "extensionAttribute14"
Angiver navnet på den AD-brugerattribut, som indeholder brugerens organisatoriske placering ("sti") fra MO.

## Funktionalitet

En normal afvikling af scriptet vil herefter gøre flg.:

1. Indlæse alle AD-brugere i og under rodenheden ($SettingOURoot)
2. For hver af disse AD-brugere tjekkes det, om brugeren allerede findes i en OU, der svarer til brugerens organisatoriske placering i MO (= den sti, der evt. står i $SettingAutoritativOrg.) AD-brugere uden en MO-sti gøres der ikke yderligere ved.
* Hvis AD-brugeren er sat som inaktiv (Enabled = $false) flyttes AD-brugeren til OU'en for inaktive brugere ($SettingOUInactiveUsers.)
* Ellers flyttes AD-brugeren til en OU svarende til MO-stien. Såfremt der mangler OU'er i AD, oprettes disse. Dette sker under roden angivet i $SettingOURoot.
3. Slutteligt fjernes alle tomme OU'er under rodenheden ($SettingOURoot), dog med undtagelse af enheden til inaktive brugere ($SettingOUInactiveUsers.)

Processen i skridt 2.2 kan illustreres således:

Lad os sige at AD-brugeren "bent" har MO-stien "Kommune > Afdeling 1 > Enhed A". I AD'et findes kun "Kommune" under rodenheden. Der vil så blive oprettet OU'er for hhv. "Afdeling 1" og "Enhed A", således at "Kommune" indeholder "Afdeling 1", der igen indeholder "Enhed A". AD-brugeren "bent" vil så blive flyttet til "Enhed A".

For at teste, mv. er det også muligt at afvikle scriptet for en enkelt AD-bruger. Denne AD-bruger kan befinde sig hvorsomhelst i AD'et. Skridt 1 vil så skippes, mens skridt 2, 2.1/2.2 og 3 udføres for den angivne AD-bruger.

## Kilde

https://github.com/OS2mo/ps-services/blob/master/Holstebro/ADStruktur.ps1
