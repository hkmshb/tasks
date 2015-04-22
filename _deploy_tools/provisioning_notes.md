Provisioning a new site
=======================

The notes herein are particular to using webfaction for deployment.

## Required packages:

* Apache 2.4    
* Python 3      
* Git           
* pip           
* virtualenv

Fortunately, on webfaction all the required packages are already installed
and available.


## Apache config
Webfaction provides a default, working httpd.conf configuration file for its setup. However the target deployment vias a little away from this setup by using virtualenv. Thus all WSGI related entries in httpd.conf needs updating to use the virtualenv. Furthermore, a local staging is performed using virtualbox virtualization with a setup which mimics that of webfaction; for these more entries are required to provide the Directory and Alias directives in order for the application and static resources to be served.

* see httpd-wsgi-extra.template.conf
* see httpd-local-extra.template.conf
* replace $USR with username, $SITENAME with webfaction app name and $PJTNAME with django project name.


## Folder structure:
Assume we have a user account at /home/username

/home/username
+-- webapps
    +-- SITENAME
        +-- apache2         # webfaction
        +-- bin             # webfaction
        +-- database        
        +-- lib             # webfaction
        +-- source
        +-- static
        +-- virtualenv

 