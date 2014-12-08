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

Some local variable in the .ansible.cfg

	hostfile       = $HOME/.inventory/
	library_path   = /usr/share/ansible/atg_modules
	remote_tmp     = $HOME/.ansible/tmp

You can overide the location of the hostfile inventory using: 

	ansible-playbook -i <path to inventory directory>  <playbook>

Create a minimum of three virtual machines however five works much better

	az1-atg-dcore-01
	az1-atg-dcore-02
	az1-atg-dcore-03
	az1-atg-dcore-04
	az1-atg-dcore-05

The virtual machines *must* be running the latest Debian "jessie"
release (aka "testing").  For instructions on how to upgrade HP Cloud
"wheezy" images to "jessie", see
[HOWTO-build-testing-image](blob/devel/HOWTO-build-testing-image.md). 

Add the VM hosts ip's to your ~/.ssh/config. 
   
	ansible-playbook inventory.yml

This will output a ssh_config file that you can then append to your current
~/.ssh/config

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
    	IdentityFile ~/.ssh/id_rsa
    	IdentitiesOnly yes

To make fleetctl work later please copy the ssh public key you want for 
the core user. Fleetctl connects over ssh and expects the private key to be 
loaded into an ssh-agent.

    ~/.ssh/id_core_rsa.pub

This will then be copied over to the 'core' user later.

Next use the `dockerdna-install.yml` playbook to install the Docker
DNA components onto the running, bare cluster of Debian hosts:

    ansible-playbook dockerdna-install.yml
    
## Ansible automation

The previous steps of launching nova instances, upgrading them, and installing the software can be accomplished using Ansible. 

The steps are essentially:

1. Create a nova inventory file
2. Launch instances
3. Generate an inventory file for the instances
4. Run dist-upgrade on the instances
5. Run demo-install on the instances

### Create a nova inventory file

Create an inventory file with your nova credentials. This file will only need localhost because that is where it will run against to launch the instances

Note: the text ```$inventory_dir``` is used in these steps. This is where you chose to keep your inventory files.


	[servers:vars]
	etcd_discovery_file="~/DeCore/discovery-west"
	
	[nova]
	localhost ansible_connection=local
	
	[nova:vars]
	nova_username="your-username"
	nova_password='your-password'
	nova_tenant_name="your-tenant-name"
	nova_region_name="region-a.geo-1"
	nova_auth_url="https://region-a.geo-1.identity.hpcloudsvc.com:35357/v2.0/"
	nova_image_id=name-of-an-image-to-boot
	nova_key=ssh-key-for-login
	nova_name=name-of-server
	nova_flavor_id=101
	num_instances=5
	ssh_user=root

	# where to write out your ssh config
	ssh_config="~/.ssh/config.d/01_ssh_config-west"
	
	# where to write out your inventory file. This is should 
	# be the same directory as where this file should 
	# live also
	nova_inventory_dir="~/inventory-west"
	

Once this inventory file is created, it should be placed in $inventory_dir/inventory_nova for ease-of-use.

Now the playbook to launch the instances can be run. By default, 7 instances will be launched. A different number can be chosen as well by specifying the variable ```num_hosts```

Enter the DeCore repository.
 
Default:

    you@az1-cpu001:~/DeCore$ ansible-playbook -i $inventory_dir/inventory_nova -vvvv -e setup-hosts.yml

Only 3 hosts:

    you@az1-cpu001:~/DeCore$ ansible-playbook -i $inventory_dir/inventory_nova -vvvv -e num_hosts=3 setup-hosts.yml

It is now possible to verify using the nova client that the instances are running:

    you@az1-cpu001:~/DeCore$ nova list

### Generate an inventory file for the nova compute instances

Run the playbook to generate an inventory file named ```inventory_username``` one directory up in your ```$inventory_dir```, "username" being what the nova username is:

    you@az1-cpu001:~/DeCore$ ansible-playbook -i $inventory_dir/inventory_nova -vvvv inventory.yml

Verify the inventory file is created:

   you@az1-cpu001:~/DeCore$ ls -l $nova_inventory_dir/inventory_username

Note: this will also create an ssh config snippet for these hosts to manually
add to your .ssh/config file. It is placed in your home directory as 
```ssh_config_dynamic_username```

### OPTIONAL (!) generate ssh config file for convenience 

This will create an ssh config file based off of the credentials above reading
what nova compute instances are running. 

IMPORTANT: this will overwrite your existing ssh config which is why it is optional. 
The previously-mentioned inventory role creates the same file but places it in your
home directory for you to manually add it. This is a convenience role.

    you@az1-cpu001:~/DeCore$ ansible-playbook -i ../inventory/inventory_nova -vvvv ssh_config.yml

### Run the dist-upgrade 

    you@az1-cpu001:~/DeCore$ ansible-playbook -i ../inventory/inventory_username dist-upgrade.yml

### Run demo-installer

    you@az1-cpu001:~/DeCore$ ansible-playbook -i ../inventory/inventory_username demo-installer.yml


## Testing Docker

This section will cover how to test Docker both by hand as well as using Ansible

### By Hand

Simple manual test to see if you can launch a single hello-world container

Ensure docker is running:

    $ sudo docker ps
    CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES

Of course, there are no images available. Simply by running a given image, Docker will pull it from the registry. There is a hello-world image available that allows you to test your docker installation in addition to claiming you have run a container!

Run the container, and the output will be the following:

    $ docker run hello-world
    Unable to find image 'hello-world' locally
    Pulling repository hello-world
    ef872312fe1b: Download complete
    511136ea3c5a: Download complete
    7fa0dcdc88de: Download complete
    Hello from Docker.
    This message shows that your installation appears to be working correctly.
    
    To generate this message, Docker took the following steps:
     1. The Docker client contacted the Docker daemon.
     2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
        (Assuming it was not already locally available.)
     3. The Docker daemon created a new container from that image which runs the
        executable that produces the output you are currently reading.
     4. The Docker daemon streamed that output to the Docker client, which sent it
        to your terminal.
    
    To try something more ambitious, you can run an Ubuntu container with:

     $ docker run -it ubuntu bash
    
    For more examples and ideas, visit:
     http://docs.docker.com/userguide/

## Testing Docker with Ansible

There is a role available in the DeCore repository named "docker_verification". It can be run using the docker.yml playbook. This playbook uses the docker_verification role which has the following steps:

1. Install Python easy_install
2. Install PIP
3. Upgrade six.py (big headache on Debian, this is the simple solution and has to be done)
4. Install the Docker python client 
5. Launch 10 (or N) docker containers
6. Run through the ansible facts from Docker, looping through each container. A large dictionary of information will be returned
7. Shuts down the containers

Note: This assumes the previous steps of launching the instances, dist-upgrade, and demo-installer have been run. 

To run it only on one host - this can take a while, run the following, specifying ```host``` on the command line:

    you@az1-cpu001:~/DeCore$ ansible-playbook -i ../inventory/inventory_username -e hosts=test-dcore-6 docker.yml

Or to run 20 containers:

    you@az1-cpu001:~/DeCore$ ansible-playbook -i ../inventory/inventory_username -e hosts=test-dcore-6 docker.yml -e container_count=20 

To run it on all hosts:

    you@az1-cpu001:~/DeCore$ ansible-playbook -i ../inventory/inventory_username

Expect to see output of the package installation, launching of containers, then a huge dictionary for you to verify your setup, then the containers being shut down.
