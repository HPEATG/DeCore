DeCore
======

Setup etcd, docker, fleet, and others on Debian testing

Steps:

Install Ansible

Source source_me file

Create a minimum of three virtual machines named

  az1-atg-dcore-01
  az1-atg-dcore-02
  az1-atg-dcore-03

Add the VM hosts ip's to your ~/.ssh/config

  Host az1-atg-dcore-01
  Hostname 15.x.x.x
    User debian
    IdentityFile ~/.ssh/id_rsa-hp-20120401
    IdentitiesOnly yes
  
  Host az1-atg-dcore-02
  Hostname 15.x.x.x
    User debian
    IdentityFile ~/.ssh/id_rsa-hp-20120401
    IdentitiesOnly yes
  
  Host az1-atg-dcore-03
  Hostname 15.x.x.x
    User debian
    IdentityFile ~/.ssh/id_rsa-hp-20120401
    IdentitiesOnly yes
    
ansible-playbook demo-installer.yml

You man need to re-run the above if there are failures with the dist-upgrade process. Sometimes packages are missing on the mirror you randomly hit. 

ansible-playbook demo-installer.yml


