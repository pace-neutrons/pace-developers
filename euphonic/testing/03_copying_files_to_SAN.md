There is a SAN for storing large files for testing at
\\isis.cclrc.ac.uk\Shares\PACE_Project_Tool_Source

## Copying files

### From Linux - general case

**1. Mount the share**

Note this requires root access. If you don't have root access on the system you
want to copy from you'll have to find a way round this, e.g. see
[IDAaaS](#IDAaaS).

First create a credentials file e.g. `pace_mount.creds`
```
domain=clrc
username=fedid
```
Create a folder to use as a mountpoint
```
mkdir pace_mount
```
Then mount the share

```
mount -v -t cifs -o _netdev,rw,soft,vers=3.0,credentials=/root/pace_mount.creds,file_mode=0600,dir_mode=0700 //isis.cclrc.ac.uk/Shares/PACE_Project_Tool_Source /root/pace_mount

```

If the above fails, make sure you have `cifs-utils` installed
```
yum -y install cifs-utils
```

**2. Copy with rsync**
```
rsync -v -r --append-verify quartz/really_big_folder/ pace_mount/
```
If connection is lost or times out, `rsync` can resume where it left off if you
use `append-verify`. Just rerun the same command and it will copy over
incomplete or missing files. Run the command again to check everything worked
correctly, and if there are no more files in the returned file list (can be seen
with `-v`) the transfer is complete.

### IDAaaS
To copy from IDAaaS, I contacted support@analysis.stfc.ac.uk. Their solution was
to create an SCD cloud machine with CEPH (the file storage containing the
experimental folders) mounted to which I had root access.