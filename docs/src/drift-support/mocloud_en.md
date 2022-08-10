---
title: MoCloud_en
--- 
## Prerequisites for operation of MO in Azure

### VPN device
For security reasons the OS2mo-cloud solution requires all communication between
your network and OS2mo happens via a site-to-site VPN-tunnel. Typically it will be possible to use 
an existing firewall or router, but it is also possible to use a dedicated device. 

The VPN device need a permanent public IPv4 address, which you will provide to Magenta in order 
to establish the connection.

Magenta uses Azure VPN Gateway, which supports devices with support for IPSEC, IKE v2 and 
Routebased. Supported devices include among others: 

- Cisco ASA and ASR
- Juniper SRX 
- Check Point
- Fortigate
- pfSense

Specific installation of VPN endpoints and network configurations are coordinated 
in detail with Magenta.

### Routing
When a tunnel has been established via the VPN device a route will need to be created from 
your servers' IP network to Microft's Azure Network, so that traffic to here is routed through the 
VPN device. This might automatically happen during the installation of the VPN device, 
depending on which type is used.

### Firewall-configuration
It must be possible to allow outgoing traffic to the OS2mo servers through the VPN tunnel. If 
integrations with on-premises services, like Active Directory, are used, incoming traffic to these 
must be possible to be allowed. Protocols that must be able to communicate are:

- LDAP
- SSH
- HTTPS

## Security

### Network communications
The connection between the OS2mo cloud application and on-premises servieces are created via an
IPsec based site-to-site virtual private network (VPN). Ie. the traffic between OS2mo and, 
for example, Active Directory happens via the public Internet, however in an encrypted tunnel 
which is only accessible via the closed network on both sides. All packages are thereby sent as 
encrypted data between the two networks.

Access from the cloud network to the on-premises network is further limited bt firewall, so that
only specifik OS2mo applications servers can communicate with the internal services.

Magenta coordinates the configuration of the access limitations on both sides of the tunnel.

### Data security
Data in the OS2mo system never leaves the virtual private networks in Microsoft Azure's 
secured data centers. Databases can exclusively be accessed from the closed and customer-
specific cloud network, and traditional access control from the applications are used. Access 
to data in block storage is limited to the application servers from which it is used.

### Magenta's access
Configuration and control of the cloud system happens via Microsoft Azure APIs, as well as, a 
web based console. The Access to these are limited according to the principle of "least 
privilege" - ie. only workers with Magenta who need to control the system and administrate the
infrastructure have access. Furthermore, access requires use of multi-factor authentication by 
the workers logging in to the Azure systems. 

When Magenta's workers require access to the OS2mo application server it happens on a 
seperate VPN connection, via a server placed in the closed cloud network. Here access is 
limited with firewalls so that the workers can only access the required services and not, for 
example, communicate with servers in the on-premises network.

### Compliance 

#### Use of a cloud provider
The Provider has the Customer's general approval to use sub-providers to act as host for 
Service and attached data. If sub-providers are used, the Provider must ensure, that a lawful 
basis of transfer exists at all times. By signing the terms the Provider has specified the use of 
the following cloud service provider:

```{.text}
Microsoft Corporation

One Microsoft Way, Redmond, WA 98052, USA

Basis of transfer: The EU-commision's standard contract, clauses and 
certification under the EU-U.S. Privacy Shield Framework
```

The Provider agrees to a written data handling agreement with any sub-provider, in which, the 
sub-provider must at least adhere to the same obligations the Provider has accepted in this
data handling agreement with the Customer. By accepting the data handling agreement the 
Customer has approved that Microsoft is used as a sub-provider. This approval includes the 
terms that the Provider has accepted as part of the subscription of Microsoft Azure. 
Microsoft's data handling terms can at any time be found on www.microsoft.com under "Online 
Services Data Protection Addendum (DPA)".

The Customer is entitled to, at any time, recieve af copy  of the Provider's contract with a 
sub-privider connected to the data protection obligations in this agreement. The Provider will 
inform the Customer with a written message within a month when there are changes or 
additions to the list of sub-providers. If the Customer has fair and specific reasons to not 
accept the Provider's use of a new sub-provider, the Customer is entitled to cancel the 
agreement with no warning.

#### Transfer to a third country
Transfer of personal information to a third country (countries outside the European Union ("EU)
and the European Economical Community("EEC")) can only be done in accordance with the 
Customer's instructions. The Customer must keep a record of sufficient knowledge of the, at 
any time, current legal basis for transferring personal data outside EU/EEC. By accepting the 
terms of this data handling agreement the Provider states that the Provider uses data handlers
outside the EEC, listed in section 5 over. The data controller has confirmed that the use of this
sub-provider is covered by instruction. 

#### Documentation and monitoring
By the Customer's request the Provider must deliver all necessary information to the Customer, 
which enables the Customer to audit the accordance of the Provider's obligations according to 
this data handling agreement. The Provider must give access to the Provider's physical 
facilities and assists with audits, including inspection carried out by the Customer or the 
Customer's accountant or by another external consultant imposed by the Customer. 
Furthermore the Provider must give all necessary information connected to the data handling 
assignments to the public authorities, The Customer and the Customer's external consultants, 
to the extent that is required for their tasks. The Provider can by written agreement invoice 
the Customer with fair remuneration for this help. The Provider is obligated to supervise it's sub-
providers on the same terms as the Customer's supervision of the Provider. The Provider is 
obligated to present the Customer with documentation to prove that the Provider complies with 
it's supervisory obligation.

## Technology, setup and correlation

### Operation of OS2mo services
OS2mo services and components for integration are executed from virtual maschines on 
Microsoft Azure via three clusters through Azure Kubernetes Service (AKS). Deployment will
also happen with Terraform and Flux CD.

### Databases
A managed PostgreSQL database (Azure Database for PostgreSQL flexible server) is used for 
the mox/lora database. ([1] on the diagram]) with automatic backups.

In the current configurations the database is executed in a container with a custom 
PostgreSQL image. Furthermore the advantages of a managed database kan be used - 
including automatic backup and maintenance. 

### Network and VPN
The individual customer's systems, ie. application servers and databases, are executed in 
segmented networks in Azure, where each customer has their own VPC, or a subnet in a shared 
VPC.

Azure VPN Gateway is used to create a secure connection between the customer's network and
VPC/subnet in Azure [2]. The connection works with devices and services which support IPsec
and IKE version 1 and 2. 

The customer therfore must set up a firewall/gateway which keeps a constant connections to 
the network in Azure [3]. In some cases the customers will potentially already have a supported 
unit which can be used, but that is not necessarily the case.

### Server for AD integration
The OS2mo integration for Active Directory requires access to the customer's domain server. 
This connection is set op together with the customer.

Magenta provides general instructions for this setup.

### Environments
In the current configurations there are three environments: dev, test and prod. To start with 
each customer receives the number of instances/servers the installation requires.

### Magenta's access to the systems
A so-called "road warrior" VPN setup is created, where each developer connects directly to a 
VPN server placed in the customer's VPC-subnet. It will be possible to connect to all 
customers' environments with the same client software, albeit with different profiles for each 
customer.

OpenVPN works well for this purpose. Alternatively, for example, Wireguard or Pritunl could be 
used.

### Security
The solution is based on all the network services being encapsulated in a virtual private 
network in order to directly communicate with each other without further authentication or 
authorization. In that sense it is a traditional perimeter-based "network defense", 
equivalent to when a customer for example executes the solution in their own data center.

The difference is that the network communication in this solution is sent encrypted via the
public Internet. Unlike internally on a private network in one's own data center, where the 
traffic never hits the Internet. Ie. the central focus related to security are VPC and the
VPN endpoints:

-  The VPC network that Azure ExpressRoute connects to. Is segmented with one network 
   per customer.
-  VPC endpoint. Configured to the individual customer's local gateway, with a specific IP and 
   shared secret, which is stored encrypted.
-  "Road warrior" VPN for Magenta's access. Access control with two-factor login.
