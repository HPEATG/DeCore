DeCore
======

Setup etcd, docker, fleet, and others on Debian testing

Steps:

Install Ansible 1.8

	 sudo pip uninstall ansible
	 git clone https://github.com/ansible/ansible.git --recursive ansible-src
	 cd ansible-src
	 git pull --rebase
	 git submodule update --init --recursive
	 sudo python setup.py install

Source source_me file

	source source_me

Create a minimum of three virtual machines named

	az1-atg-dcore-01
	az1-atg-dcore-02
	az1-atg-dcore-03

Add the VM hosts ip's to your ~/.ssh/config. Modify this to the IP's you want to connect to.

	Host az1-atg-dcore-01
	Hostname x.x.x.x
    	User debian
    	IdentityFile ~/.ssh/id_rsa
    	IdentitiesOnly yes
  
	Host az1-atg-dcore-02
	Hostname x.x.x.x
    	User debian
    	IdentityFile ~/.ssh/id_rsa
    	IdentitiesOnly yes
  
	Host az1-atg-dcore-03
	Hostname x.x.x.x
    	User debian
    	IdentityFile ~/.ssh/id_rsa-hp
    	IdentitiesOnly yes

The run this playbook to upgrade from Debian Stable to Testing. A must for systemd.

	ansible-playbook dist-upgrade.yml

You man need to re-run the above if there are failures with the dist-upgrade process. Sometimes packages are missing on the mirror you randomly hit. 


	ansible-playbook demo-installer.yml


.h2 Testing Docker

This section will cover how to test Docker both by hand as well as using Ansible

Simple manual test to see if you can launch a single container running ubuntu

Ensure docker is running:

    $ sudo docker ps
    CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES

Of course, there are no images available. Simply by running a given image, Docker will pull it from the registry:
    $ sudo docker run -it ubuntu /bin/bash
    Unable to find image 'ubuntu' locally
    Pulling repository ubuntu
    5506de2b643b: Download complete
    511136ea3c5a: Download complete
    d497ad3926c8: Download complete
    ccb62158e970: Download complete
    e791be0477f2: Download complete
    3680052c0f5c: Download complete
    22093c35d77b: Download complete
    root@c5f2511a4dff:/# ls
    bin  boot  dev  etc  home  lib  lib64  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var


