# About LSC Script PAPERCUT

Those scripts hase been created to sync data between LDAP tree to PAPERCUT solutions
Syncing operation from LDAP providing by Papercut Aren't enough customizable.
In my case I need to make some transformation on some attributs
I found a solution by using LSC (https://lsc-project.org/doku.php) which could called some script see : https://lsc-project.org/documentation/plugins/executable

# How to Use it :

You need to :
- Active XML-RPC interface on PaperCut
- get a service account on LDAP Tree
- LSC Ldap Synchronization Connector installled with exe plugin 

## how to active XML-RPC interface
https://www.papercut.com/support/resources/manuals/ng-mf/common/topics/tools-web-services.html

## how to install lsc-script-papercut

### install
```
apt-get install python3 virtualenv python3-virtualenv
git clone https://github.com/gallak/lsc-script-papercut.git
cd lsc-script-papercut
virtualenv -p python3 .
source ./bin/activate
pip install -r requirements.txt
```

### Configuration

see inside `lsc` subdirectory
you need to configure the script trough variables exported


# More details

## More details of XMLRPC Perpercut API

https://gist.github.com/damienatpapercut/67dee5d06ed47b3283ca
Attributes availbale
balance', 'card-number', 'card-pin', 'department',
  'disabled-net', 'disabled-print', 'email', 'full-name', 'notes',
  'office', 'print-stats.job-count', 'print-stats.page-count',
  'net-stats.data-mb','net-stats.time-hours','restricted']

# how to add username aliasing
https://www.papercut.com/support/resources/manuals/ng-mf/applicationserver/topics/user-username-aliasing.html

# how to active XML-RPC interface
https://www.papercut.com/support/resources/manuals/ng-mf/common/topics/tools-web-services.html


# HOW it runs ?

## example in DEBUG and DRY-RUN mode

You need run with one thread `-t 1` options

```
lsc -f . -s all -c all -n -t1

INFO  - Starting sync for Users
DEBUG - Update condition false. Should have modified object uid=blueelephant502,ou=people,dc=demo,dc=fusion
dn: uid=blueelephant502,ou=people,dc=demo,dc=fusion
changetype: modify
replace: notes
notes: le mot de passe de blueelephant502 est poopy avec un modif en plus c'est cool
-
ERROR - Entries count: 0
DEBUG - Create condition false. Should have added object uid=greenduck658,ou=people,dc=demo,dc=fusion
dn: uid=greenduck658,ou=people,dc=demo,dc=fusion
changetype: add
notes: Ceci est une2 eme  modification
username-alias: starter
primary-card-number: teacher123454
office: L3C1
secondary-card-number: 0000carteproxlsb
department: SCHOOL
email: aaliyah.green@example.com
full-name: Aaliyah Green
INFO  - All entries: 3, to modify entries: 2, successfully modified entries: 0, errors: 0
INFO  - Starting clean for Users
DEBUG - Delete condition false. Should have removed object uid=whitebird737,ou=fake,dc=dn
-- clean phase
dn: uid=whitebird737,ou=fake,dc=dn
changetype: delete

INFO  - All entries: 3, to modify entries: 1, successfully modified entries: 0, errors: 0

real	0m15.143s
user	0m13.919s
sys	0m1.138s


```

