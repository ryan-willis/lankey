sysarch=$(uname -m)
arch=${1:-$sysarch}

rm -fr dist*/* && \
    pyinstaller --distpath ./dist-main/ --add-data="scripts:scripts" --target-arch $arch --noconfirm -i assets/AppIcon.icns -w -s LANKey.py && \
    rm -fr dist-main/LANKey && \
    ln -s /Applications dist-main/ && \
    hdiutil create -volname LANKey -ov -format UDZO -srcfolder ./dist-main ./dist-main/LANKey.dmg  && \
    pyinstaller --distpath ./dist-receiver/ --add-data="scripts:scripts" --target-arch $arch --noconfirm -i assets/AppIcon.icns -w -s LANKeyReceiver.py && \
    rm -fr dist-receiver/LANKeyReceiver && \
    hdiutil create -volname LANKeyReceiver -ov -format UDZO -srcfolder ./dist-receiver ./dist-receiver/LANKeyReceiver.dmg