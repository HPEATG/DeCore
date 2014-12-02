HOW-TO Build a Debian Testing (Jessie) Image
============================================

How to build a stock Debian Testing (Jessie) image required for setting up etcd, docker, fleet, and others.

Steps: 

0. Boot from a Debian Wheezy Image.

1. Login to the host.

2. Verify GRUB is installed as the bootloader:

   ```
   # dpkg -l | grub
   ii  grub-common       1.99-27+deb7u2  amd64   GRand Unified Bootloader (common files)
   ii  grub-pc           1.99-27+deb7u2  amd64   GRand Unified Bootloader, version 2 (PC/BIOS version)
   ii  grub-pc-bin       1.99-27+deb7u2  amd64   GRand Unified Bootloader, version 2 (PC/BIOS binaries)
   ii  grub2-common      1.99-27+deb7u2  amd64   GRand Unified Bootloader (common files for version 2)
   
   ```
   
   a. If the output of `dpkg -l | grep grub` is nothing then install
      GRUB, specifically the 'grub2' meta-package which will pull all
      the necessary packages in:
      
      ```
      sudo apt-get update
      sudo apt-get install grub2
      ```
   

3. Upgrade from Wheezy (stable) to Jessie (testing):

   a. Edit /etc/apt/sources.list replacing it with:

      ```
      deb http://http.debian.net/debian testing main
      deb http://http.debian.net/debian testing-updates main
      deb http://security.debian.org testing/updates main
      
      deb-src http://http.debian.net/debian testing main
      deb-src http://http.debian.net/debian testing-updates main
      deb-src http://security.debian.org testing/updates main
      ```
    
   b. Upgrade to Testing (Jessie) with the following sequence of commands run as root:

      ```
      sudo apt-get update                           ## Update cache
      sudo apt-get -y --download-only dist-upgrade  ## pre-download
      sudo apt-get -y -f dist-upgrade               ## Force Upgrade
      ```

      Note: When you are asked about the boot-loader, just accept defaults
   
   c. The dist-upgrade may fail, repeat as needed
   
      ```
      sudo apt-get -y -f dist-upgrade               ## repeat until
                                                    ## successful 
      sudo apt-get -y autoremove                    ## clean-up
      ```

4. Reset the machine-id and install (ATG) custom script to reset the 
   machine-id.

   a. Create the `/etc/systemd/scripts` directory:

      ```
      sudo mkdir /etc/systemd/scripts
      sudo chmod 755 /etc/systemd/scripts
      ```

   b. Place the following script into `/etc/systemd/scripts/reuuid` and
      set the permissions for execute (i.e. 0755):
      
      ```
      #!/bin/sh
      
      if [ ! -f /etc/machine-id ] ||
      [ ! -f /var/lib/dbus/machine-id ]; then
         /bin/systemd-machine-id-setup
         /usr/bin/dbus-uuidgen --ensure
         echo "Created machine-id: `cat /etc/machine-id`"
      fi
      ```
   
   c. Place the following systemd unit file into
      `/etc/systemd/system/reuuid.service` and set the permissions to
      read (0644):
      
      ```
      [Unit]
      Description=Reset machine UUID files
      DefaultDependencies=no
      Conflicts=shutdown.target
      After=systemd-remount-fs.service
      Before=systemd-journald.service
      systemd-tmpfiles-setup-dev.service
      systemd-tmpfiles-setup.service
      ConditionPathIsReadWrite=/etc
      
      [Service]
      Type=oneshot
      RemainAfterExit=yes
      ExecStart=/etc/systemd/scripts/reuuid
      StandardOutput=tty
      StandardError=tty
      
      [Install]
      WantedBy=sysinit.target
      WantedBy=systemd-journald.service
      WantedBy=systemd-tmpfiles-setup.service
      WantedBy=systemd-tmpfiles-setup-dev.service
      ```

   d. Remove the existing machine-id files:
   
      ```
      sudo rm /etc/machine-id
      sudo rm /var/lib/dbus/machine-id
      ```
      
   e. (verify)
      1. Reboot
      2. Verify both `/etc/machine-id` and `/var/lib/dbus/machine-id` 
         are again populated, and with the same value.
      3. Remove both files as done in step d. above.

6. Upgrade complete.  Shutdown the host for imaging
   
    ```shutdown -h now```

7. "Create Snapshot" of the insance from the Horizon console.
   - alternate:  ```nova image-create```  -- see nova command ```help```.

8. Done.

