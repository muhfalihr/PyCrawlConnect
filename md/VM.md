# INSTALLATION & CONFIGURATION VIRTUAL MACHINE

### INSTALL 1 VM FOR KAFKA SERVER, AND 3 VMs FOR ELASTICSEARCH SERVER. !!!

## I. Install VM Virtual Box as Hypervisor

- install VM virtual box in Terminal and Setup Virtual Machine

  ```sh
  sudo apt install virtualbox
  ```

- Open the VirtualBox Software.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/1.png?raw=true)

- Click **New**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/Screenshot%20from%202023-12-25%2011-00-11.png?raw=true)

- Provide the name and type of operating system to be installed. Click **Next**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/Screenshot%20from%202023-12-25%2011-01-12.png?raw=true)

- Set the Memory Space to default (1024 MB). Click **Next**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/Screenshot%20from%202023-12-25%2011-01-58.png?raw=true)

- Select **Create a virtual hard disk now**. Click **Create**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/Screenshot%20from%202023-12-25%2011-02-02.png?raw=true)

- Select **VDI (Virtual Disk Image)**. Click **Next**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/Screenshot%20from%202023-12-25%2011-02-22.png?raw=true)

- Select **Dynamically allocated**. Click **Next**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/Screenshot%20from%202023-12-25%2011-02-26.png?raw=true)

- Set File location and size (default = 12.00 GB). Click **Create**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/Screenshot%20from%202023-12-25%2011-02-30.png?raw=true)

- Click the three line icon. Click **Network**. (to create a VirtualBox Host-Only Ethernet Adapter).

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/Screenshot%20from%202023-12-25%2011-03-33.png?raw=true)

- Click **Create**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/Screenshot%20from%202023-12-25%2011-03-51.png?raw=true)

- Click the three line icon. Click **Welcome**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/2.png?raw=true)

- Click **Setting**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/Screenshot%20from%202023-12-25%2011-04-11.png?raw=true)

- Click the **System** menu. Uncheck **Floppy**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/Screenshot%20from%202023-12-25%2011-04-43.png?raw=true)

- Click the **Storage** menu. Click the empty CD icon. Select the Optical Drive with the desired .iso file. [Official website to download Ubuntu server iso](https://ubuntu.com/download/server).

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/Screenshot%20from%202023-12-25%2011-05-12.png?raw=true)

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/Screenshot%20from%202023-12-25%2011-05-38.png?raw=true)

- Select the **Network** menu. For **Adapter 1** as **NAT**. For **Adapter 2** as **Host-only Adapter**. (vboxnet1). Click **OK**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/Screenshot%20from%202023-12-25%2011-06-09.png?raw=true)

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/Screenshot%20from%202023-12-25%2011-06-22.png?raw=true)

- Click **Start**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/Screenshot%20from%202023-12-25%2012-01-17.png?raw=true)

- Specify language. Select **English**. Then press **ENTER**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/3.png?raw=true)

- Select **Continue without updating**. Then press **ENTER**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/4.png?raw=true)

- Keyboard configuration. Select **Done**. Then press **ENTER**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/4.png?raw=true)

- Network connections. Select **Done**. Then press **ENTER**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/6.png?raw=true)

- Configure proxy. Select **Done**. Then press **ENTER**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/7.png?raw=true)

- Configure Ubuntu archive mirror. Select **Done**. Then press **ENTER**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/8.png?raw=true)

- Guided Storage configuration. Select **Done**. Then press **ENTER**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/9.png?raw=true)

- Storage configuration. Select **Done**. Then press **ENTER**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/10.png?raw=true)

- Confirm destructive action. Select **Continue**.Then press **ENTER**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/11.png?raw=true)

- Profil setup. Determine and fill in **your name**, **your server's name**, **pick a username**, **choose a password**, **confirm your password**. Select **Done**. Then press **ENTER**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/12.png?raw=true)

- SSH Setup. Select **Done**. Then press **ENTER**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/13.png?raw=true)

- Featured Server Snaps. Select **Done**. Then press **ENTER**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/14.png?raw=true)

- Installing system.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/15.png?raw=true)

- Select **Cancel update and reboot** / **Reboot**. Then press **ENTER**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/16.png?raw=true)

- Please remove the installation medium, then press **ENTER**.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/17.png?raw=true)

- Installation is complete, log in by entering your username and password.

  ![](https://github.com/muhfalihr/mystorage/blob/master/vm/18.png?raw=true)

## II. Remote Server

- Change or set the hostname.

  ```sh
  hostnamectl set-hostname hostname
  ```

- Edit the hosts file and add:

  ```sh
  nano /etc/hosts
  # <ip-host> hostname
  ```

- Install OpenSSH server.

  ```sh
  apt install openssh-server
  ```

- Edit the sshd_config file:

  ```sh
  nano /etc/ssh/sshd_config
  # Uncomment PermitRootLogin
  # Then type PermitRootLogin yes
  ```

- Restart the SSH (Secure Shell) service.

  ```sh
  systemctl restart sshd
  ```

- Check the current user.

  ```sh
  whoami
  ```

- Determine the password for the user.

  ```sh
  passwd username
  ```
