printf "\033c\n "
printf "\033[40;37m\ngive me disk image name ? "
read h
printf "\033[40;37m\ngive me disk image size in MB ? "
read g
dd if=/dev/zero of=$h bs=1M count=$g status=progress
chmod 777 $h
echo '.........................................'
mkfs.ext2 -b 1024 -I 128 -O none  $h
chmod 777 $h
echo '.........................................'
mkdir /mnt/rams 2>/dev/null
sudo umount /mnt/rams 2>/dev/null
sudo mount -o loop $h /mnt/rams
echo '.........................................'
printf "\033[40;37m\ngive me the files to include in main root ? "
read a
for b in $a
do
    sudo cp $b /mnt/rams
    sudo chmod 777 /mnt/rams/$b
done
mkdir /mnt/rams/dev 2> /dev/null
mkdir /mnt/rams/mnt 2> /dev/null
mkdir /mnt/rams/etc 2> /dev/null
mkdir /mnt/rams/dev 2> /dev/null
mkdir /mnt/rams/bin 2> /dev/null
mkdir /mnt/rams/sbin 2> /dev/null
mkdir /mnt/rams/usr 2> /dev/null
mkdir /mnt/rams/root 2> /dev/null
mkdir /mnt/rams/root/etc 2> /dev/null
mkdir /mnt/rams/root/dev 2> /dev/null
mkdir /mnt/rams/root/bin 2> /dev/null
mkdir /mnt/rams/root/sbin 2> /dev/null
mkdir /mnt/rams/root/usr 2> /dev/null
mkdir /mnt/rams/root/run 2> /dev/null
mkdir /mnt/rams/root/proc 2> /dev/null
mkdir /mnt/rams/root/sys 2> /dev/null
mkdir /mnt/rams/proc 2> /dev/null
mkdir /mnt/rams/sys 2> /dev/null
mkdir /mnt/rams/boot 2> /dev/null
mkdir /mnt/rams/run 2> /dev/null
printf "" > /mnt/rams/dev/console
chmod 777 /mnt/rams/* 2> /dev/null
sudo umount /mnt/rams 2>/dev/null
echo '.........................................'
g=38
h=boot.img
dd if=/dev/zero of=$h bs=1M count=$g status=progress
chmod 777 $h
echo '.........................................'
mkfs.fat -F 12 $h
chmod 777 $h
echo '.........................................'
syslinux  $h
chmod 777 $h
echo '.........................................'
echo "o" | mcopy -i $h syslinux.cfg ::/syslinux.cfg
echo "o" | mcopy -i $h initrd.img ::/initrd.img
echo "o" | mcopy -i $h vmlinuz ::/vmlinuz
echo "o" | mcopy -i $h ldlinux.c32 ::/ldlinux.c32
chmod 777 $h