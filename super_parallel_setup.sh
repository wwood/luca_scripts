#!/bin/bash

mkdir -p ~/.parallel
ln -sv ~/.parallel ~/.p #for less typing
# symlink regular servers
ls /srv/sw/luca_scripts/github_version/parallel_sshfiles/ |grep ace |grep -v mrca |sed 's/.ace.uq.edu.au//' |/srv/sw/parallel/20151122/bin/parallel -kt ln -sv /srv/sw/luca_scripts/github_version/parallel_sshfiles/{}.ace.uq.edu.au ~/.parallel/{}
# mrca servers shorten  e.g. mrca002 => m2
ls /srv/sw/luca_scripts/github_version/parallel_sshfiles/ |grep ace |grep mrca |sed 's/.ace.uq.edu.au//; s/rca00//' |/srv/sw/parallel/20151122/bin/parallel -kt ln -sv /srv/sw/luca_scripts/github_version/parallel_sshfiles/{}.ace.uq.edu.au ~/.parallel/{}

echo
echo "ssh files now setup. Next, you can add the following to your ~/.bashrc"
echo "#source superparallel bash function"
echo "source /srv/sw/luca_scripts/github_version/parallel_sshfiles/sparallel_function.bash"

echo
echo "also you'll need to setup a password-less SSH key to easy jump within luca. Run the following to set this up:"
echo "ssh-keygen -f ~/.ssh/id_rsa_intraluca -t rsa -N '' && cat ~/.ssh/id_rsa_intraluca.pub >>~/.ssh/authorized_keys"
