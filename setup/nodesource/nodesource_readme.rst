NodeJS v.8.x (LTS)
==================

Nyere NodeJS versioner er ikke includeret i Ubuntu 16.04 (LTS),
derfor bør NodeJS LTS versionen installeres via et eksternt apt repository.

Installationen af NodeJS kan udføres i følgende trin,

Tilføj nodesource public nøgle: ::

  $ cd setup/nodesource
  $ sudo apt-key add nodesource.gpg.key


Nodesource apt repository skal tilføjes: ::

  # Add list file
  $ cd setup/nodesource
  $ sudo cp nodesource-8.x.list /etc/apt/sources.list.d/nodesource-8.x.list

  # Update apt cache
  $ sudo apt-get update

Installer nodejs meta pakken: ::

  $ sudo apt-get install nodejs


Bekræft at version 8 er installeret: ::

  $ node -v
  v8.11.1

