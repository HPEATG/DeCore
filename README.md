DeCore
======

Setup etcd, docker, fleet, and others on Debian testing

Steps:

Install Ansible

	pip install ansible

Source source_me file

	source source_me

Create a minimum of three virtual machines named

	az1-atg-dcore-01
	az1-atg-dcore-02
	az1-atg-dcore-03

Add the VM hosts ip's to your ~/.ssh/config. Modify this to the IP's you want to connect to.

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

The run this playbook to upgrade from Debian Stable to Testing. A must for systemd.

	ansible-playbook dist-upgrade.yml

You man need to re-run the above if there are failures with the dist-upgrade process. Sometimes packages are missing on the mirror you randomly hit. 


	ansible-playbook demo-installer.yml


