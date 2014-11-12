HOW-TO Build a Debian Testing (Jessie) Image
============================================

How to build a stock Debian Testing (Jessie) image required for setting up etcd, docker, fleet, and others.

Steps: 

1. Boot from a Debian Wheezy Image.

2. Login to the host.

3. Edit /etc/apt/sources.list replacing it with:

    ```
    deb http://http.debian.net/debian testing main
    deb http://http.debian.net/debian testing-updates main
    deb http://security.debian.org testing/updates main
    
    deb-src http://http.debian.net/debian testing main
    deb-src http://http.debian.net/debian testing-updates main
    deb-src http://security.debian.org testing/updates main
    ```
    
4. Upgrade to Testing (Jessie) with the following sequence of commands run as root:

    ```
    apt-get update                           ## Update cache
    apt-get -y --download-only dist-upgrade  ## pre-download
    apt-get -y -f dist-upgrade               ## Force Upgrade
    ```

    Note: When you are asked about the boot-loader, just accept defaults
   
5. The dist-upgrade may fail, repeat as needed
   
    ```
    apt-get -y -f dist-upgrade               ## repeat until
                                             ## successful 
    apt-get -y autoremove                    ## clean-up
    ```

6. Upgrade complete.  Shutdown the host for imaging
   
    ```shutdown -h now```

7. "Create Snapshot" of the insance from the Horizon console.
   - alternate:  ```nova image-create```  -- see nova command ```help```.

8. Done.

Author: Eric Gustafson <gustafson@hp.com> 2014-11-11
