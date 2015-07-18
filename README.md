DeCore
======

Set up etcd, docker, fleet, and other components into a cluster on Debian-based Linux distributions

Steps:

- Install Ansible 2.0

    Linux:
  
    ```
    sudo pip uninstall ansible
    git clone https://github.com/ansible/ansible.git --recursive ansible-src
    cd ansible-src
    git pull --rebase
    git submodule update --init --recursive
    sudo python setup.py install
    ```

    OS X:
  
    ```
    brew install ansible
    ``` 


- Set up ansible config 


    Some local variable in the .ansible.cfg set to your preference

    ```
    hostfile       = $HOME/.inventory/
    library_path   = /usr/share/ansible/atg_modules
    remote_tmp     = $HOME/.ansible/tmp
    ```

    You can overide the location of the hostfile inventory using: 

    ```
	ansible-playbook -i <path to inventory directory>  <playbook>
    ```
    
- Create Security groups

  If Nova is being used to launch the instances, security groups will be needed to allow services to be accessed. There is a file ```secgroups.txt``` that contains these groups. 

```
nova secgroup-add-rule coreos tcp 22   22   0.0.0.0/0
nova secgroup-add-rule coreos tcp 8080 8080 0.0.0.0/0
nova secgroup-add-rule coreos icmp-1   -1   0.0.0.0/0
nova secgroup-add-rule coreos tcp 2380 2380 0.0.0.0/0
nova secgroup-add-rule coreos tcp 5003 5003 0.0.0.0/0
nova secgroup-add-rule coreos tcp 4001 4001 0.0.0.0/0
nova secgroup-add-rule coreos tcp 10101 10101 0.0.0.0/0
nova secgroup-add-rule coreos tcp 5000 5000 0.0.0.0/0
nova secgroup-add-rule coreos tcp 9200 9200 0.0.0.0/0
nova secgroup-add-rule coreos tcp 5001 5001 0.0.0.0/0
nova secgroup-add-rule coreos tcp 5002 5002 0.0.0.0/0
nova secgroup-add-rule coreos tcp 80   80   0.0.0.0/0
nova secgroup-add-rule coreos tcp 7001 7001 0.0.0.0/0
nova secgroup-add-rule coreos tcp 2379 2379 0.0.0.0/0
```

- Launch instances

  create a minimum of three virtual machines however five works much better. Name 
however you wish

   ```
	core-01
	core-02
	core-03
	core-04
	core-05
   ```

  
* Required OS: Debian-based systems running ```systemd```

  The virtual machines *must* be running the latest Debian "jessie" release (aka "testing").  For instructions on how to upgrade HP Cloud
"wheezy" images to "jessie", see
[HOWTO-build-testing-image](blob/devel/HOWTO-build-testing-image.md).

  Ubuntu 15.x has a running systemd as well, and these roles have been used with success on Ubuntu 15.0 

  Add the VM hosts ip's to your ~/.ssh/config. 
  
  ``` 
	ansible-playbook inventory.yml
  ```

  This will output a ssh_config file that you can then append to your current ```~/.ssh/config```

   ```
	Host core-01
	Hostname x.x.x.x
    	User debian
    	IdentityFile ~/.ssh/id_rsa
    	IdentitiesOnly yes
  
	Host core-02
	Hostname x.x.x.x
    	User debian
    	IdentityFile ~/.ssh/id_rsa
    	IdentitiesOnly yes
  
	Host core-03
	Hostname x.x.x.x
    	User debian
    	IdentityFile ~/.ssh/id_rsa
    	IdentitiesOnly yes
    ```
    To make fleetctl work later please copy the ssh public key you want for 
the core user. Fleetctl connects over ssh and expects the private key to be 
loaded into an ssh-agent.

    ```
    ~/.ssh/id_core_rsa.pub
    ```
    This will then be copied over to the 'core' user later.

    Next use the `dockerdna-install.yml` playbook to install the Docker
DNA components onto the running, bare cluster of Debian hosts:

    ```
    ansible-playbook dockerdna-install.yml
    ```
    
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

```
[servers:vars]
etcd_discovery_file="~/DeCore/discovery-west"
	
[nova_east]
localhost ansible_connection=local
	
[nova_east:vars]
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
	
# where to write out your inventory file. 
# This is should be the same directory as 
# where this file should live also
nova_inventory_dir="~/inventory-west"

# remote_user -- must have sudo
# debian
remote_user=debian
remote_home=/home/debian
  
git_name="Your Name"
git_email=your@email.address
   
```
Once this inventory file is created, it should be placed in ```$inventory_dir/inventory_nova``` for ease-of-use.

Now the playbook to launch the instances can be run. By default, 5 instances will be launched. A different number can be chosen as well by specifying the variable ```num_hosts```

Enter the DeCore repository.
 
Default:

    you@host:~/DeCore$ ansible-playbook -i $inventory_dir/inventory_nova -e target=nova_east -e setup-hosts.yml

Only 3 hosts:

    you@host:~/DeCore$ ansible-playbook -i $inventory_dir/inventory_nova -e target=nova_east -e num_hosts=3 setup-hosts.yml

It is now possible to verify using the nova client that the instances are running:

    you@host:~/DeCore$ nova list

### Generate an inventory file for the nova compute instances

Run the playbook to generate an inventory file named ```inventory_username``` one directory up in your ```$inventory_dir```, "username" being what the nova username is:

    you@host:~/DeCore$ ansible-playbook -i $inventory_dir/inventory_nova -vvvv inventory.yml

Verify the inventory file is created:

   you@host:~/DeCore$ ls -l $nova_inventory_dir/inventory_username

Note: this will also create an ssh config snippet for these hosts to manually
add to your .ssh/config file. It is placed in your home directory as 
```ssh_config_dynamic_username```

### OPTIONAL (!) generate ssh config file and entry in /etc/hosts for convenience 

This will create an ssh config file based off of the credentials above reading
what nova compute instances are running. 

IMPORTANT: this will overwrite your existing ssh config which is why it is optional. 
The previously-mentioned inventory role creates the same file but places it in your
home directory for you to manually add it. This is a convenience role.

    you@host:~/DeCore$ ansible-playbook -i ../inventory/inventory_nova -e target=nova_east ssh_config.yml
    you@host:~/DeCore$ ansible-playbook -i ../inventory/inventory_nova -e target=nova_east hosts.yml

### Run the dist-upgrade (if starting from Debian Wheezy) 

    you@host:~/DeCore$ ansible-playbook -i ../inventory/inventory_username dist-upgrade.yml

### Run demo-installer

    you@host:~/DeCore$ ansible-playbook -i ../inventory/inventory_username demo-installer.yml

### Install the cluster

    you@host:~/DeCore$ ansible-playbook -i ../inventory/inventory_username dockerdna-install.yml 


### Set fleetctl to connect to the cluster

Pick any external IP address of the machines launched. In the example below, the last machine in the list was selected.

```
user@host:~/DeCore$ nova list

+--------------------------------------+--------+--------+------------+-------------+------------------------------------------------------------+
| ID                                   | Name   | Status | Task State | Power State | Networks                                                   |
+--------------------------------------+--------+--------+------------+-------------+------------------------------------------------------------+
| c122ce91-0177-4e47-ba63-f6d4fde2b72c | core-01 | ACTIVE | -          | Running     | your-network=10.0.0.54, 15.132.53.42  |
| 46570f57-1748-414a-9fc7-c4cd59b0fca0 | core-02 | ACTIVE | -          | Running     | your-network=10.0.0.55, 15.132.44.44  |
| 85dd8f99-f020-4279-8618-83ea11bb6ada | core-03 | ACTIVE | -          | Running     | your-network=10.0.0.56, 15.132.51.117 |
| ea6ed593-69c4-4d0e-b33c-abaf43e209e5 | core-04 | ACTIVE | -          | Running     | your-network=10.0.0.57, 15.132.57.12  |
| b1ab055e-b36f-41a6-b5af-4f1b44610089 | core-05 | ACTIVE | -          | Running     | your-network=10.0.0.58, 15.132.48.123 |
+--------------------------------------+--------+--------+------------+-------------+------------------------------------------------------------+

you@host:~$ EXPORT FLEETCTL_ENDPOINT=http://15.132.48.123:4001

```

List machines in the cluster:

```
you@host:~$ fleetctl list-machines
MACHINE		IP		METADATA
46570f57...	15.132.53.42	host=core-02,ipv4_private=10.0.0.55,ipv4_public=15.132.53.42
85dd8f99...	15.132.44.44	host=core-03,ipv4_private=10.0.0.56,ipv4_public=15.132.44.44
b1ab055e...	15.132.51.117	host=core-05,ipv4_private=10.0.0.58,ipv4_public=15.132.51.117
c122ce91...	15.132.57.12	host=core-01,ipv4_private=10.0.0.54,ipv4_public=15.132.57.12
ea6ed593...	15.132.48.123	host=core-04,ipv4_private=10.0.0.57,ipv4_public=15.132.48.123
```

The cluster is now open for business!


## Testing Docker

This section will cover how to test Docker, in case you want to ensure that Docker runs as expected for single machines within the cluster, both by hand as well as using Ansible

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
2. The Docker daemon pulled the "hello-world" image from the Docker Hub. (Assuming it was not already locally available.)
3. The Docker daemon created a new container from that image which runs the executable that produces the output you are currently reading.
4. The Docker daemon streamed that output to the Docker client, which sent it to your terminal.
    
To try something more ambitious, you can run an Ubuntu container with:

    $ docker run -it ubuntu bash
    
For more examples and ideas, visit:
     [http://docs.docker.com/userguide/](http://docs.docker.com/userguide/)

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

    you@host:~/DeCore$ ansible-playbook -i ../inventory/inventory_username -e hosts=test-core-6 docker.yml

Or to run 20 containers:

    you@host:~/DeCore$ ansible-playbook -i ../inventory/inventory_username -e hosts=test-core-6 docker.yml -e container_count=20 

To run it on all hosts:

    you@host:~/DeCore$ ansible-playbook -i ../inventory/inventory_username

Expect to see output of the package installation, launching of containers, then a huge dictionary for you to verify your setup, then the containers being shut down.
