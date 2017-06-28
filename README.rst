MORA — MedarbejderOrganisation + LoRA
=====================================

To install MORA, do::

  # first, clone MORA
  sudo install -d -o $UID -g $GID /srv/mora
  git clone https://github.com/magenta-aps/mora /srv/mora

  # install dependencies
  sudo apt install python3-venv nodejs-legacy npm

  # build the application, creating the virtualenv in the progress
  /srv/mora/manage.py build
  # install gunicorn
  /srv/mora/venv-linux-cpython-3.5/bin/pip install gunicorn gevent

  # create the user and required infrastructure
  sudo adduser --system \
    --home /srv/mora \
    --shell /usr/sbin/nologin \
    --disabled-password --disabled-login \
    --ingroup www-data mora
  sudo install -d -o mora -g www-data /var/log/mora /run/mora
  sudo ln -s /srv/mora/config/mora.service /etc/systemd/system
  sudo ln -s /srv/mora/config/mora.socket /etc/systemd/system
  sudo ln -s /srv/mora/config/mora.conf /etc/tmpfiles.d

  sudo systemctl daemon-reload
  sudo systemctl enable mora.socket mora.service
  sudo systemctl start mora.service


You now have a working MoRA installation listening on a local socket.
To expose to the outside, configure Apache or nginx to forward
requests to it::

  ProxyPass /mo/ unix:/run/mora/socket|http://localhost/

Then enable the ``proxy_http`` module, and restart Apache::

  sudo a2enmod proxy_http
  sudo apache2ctl graceful

You also need to edit ``mora/lora.py`` and adjust ``LORA_URL`` to
point to your server::

  LORA_URL = "http://localhost/"

Please note that using an HTTPS URL requires a trusted certificate on
the server.
