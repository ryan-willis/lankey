<p align="center"><img src="assets/AppIcon.png" /></p>

# <p align="center">LANKey</p>
<p align="center">Invoke a script on another Mac over LAN with a single keystroke.</p>

## Local Development

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the application

```sh
source venv/bin/activate
python LANKey.py
```

### Building the release version

The build script will create standalone applications in the `dist-main` and `disc-receiver` directories.

```sh
./build.sh
```

### Special Permissions

`LANKey` requires special permissions to run. You will be prompted to for the Accessibility and Input Monitoring permissions, and when running `LANKey` or `LANKeyReceiver` for the first time, you will be prompted to allow incoming network connections.
