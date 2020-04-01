#!/bin/bash

echo "Update the System !"
apt-get update
apt-get -y upgrade


echo "Install the system package"
apt-get -y install ansible git sshpass python3 python3-pip virtualenv

echo "Change The ansible settings"
sed -i "/host_key_checking/s/^#//g" /etc/ansible/ansible.cfg

echo "Allow root login"
sed -i "s/PermitRootLogin\ prohibit-password/PermitRootLogin\ yes/g" /etc/ssh/sshd_config

echo "Change root password !"
sudo passwd root


echo "Restart SSH Deamon !"
service sshd restart

echo "Git clone code !"
git clone http://github.com/heyuantao/WebStorage.git

echo "Plase Reboot The System and Run Ansible Playbook !"
