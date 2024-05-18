sysarch=$(uname -m)
arch=${1:-$sysarch}

rm -fr dist/* && \
    pyinstaller --add-data="scripts:scripts" --target-arch $arch --noconfirm -i assets/AppIcon.icns -w -s LANKey.py && \
    rm -fr dist/LANKey && \
    ln -s /Applications dist/ && \
    hdiutil create -volname LANKey -ov -format UDZO -srcfolder ./dist ./dist/LANKey.dmg