import pathlib
import subprocess
import sys

import pynput
import rumps

import prefs
import server

scripts_dir = pathlib.Path(__file__).resolve().parent / "scripts"
port_osa = pathlib.Path(scripts_dir / "port.applescript").read_text()
action_osa = pathlib.Path(scripts_dir / "action.applescript").read_text()
message_osa = pathlib.Path(scripts_dir / "message.applescript").read_text()

args = f"{sys.argv}"

# a bit of a hack, but the bundled version of the app _won't_ have this
# and both `python LANKey.py` and `python -m LANKey` _will_ have it
APP_RUN = "LANKey.py" not in args


def osa(s: str):
    return subprocess.check_output(["osascript", "-e", s]).strip().decode()


# def valid_port(port: str):
#     try:
#         port = int(port)
#         if 1024 < port < 65536:
#             return port
#     except ValueError:
#         pass
#     return None


class LANKey(prefs.Prefs):
    def __init__(self, receiver=False):
        self.receiver = receiver
        if not self.receiver:
            self.listener = pynput.keyboard.Listener(on_press=self.on_press)
            self.refresh_timer = rumps.Timer(self.refresh_hosts, 2)
        self.hosts_list = []
        self.app = rumps.App("LANKey", "⌥")
        self.load_prefs()
        # TODO: allow the user to set the port
        # and show that port somewhere in the menu
        # port = int(valid_port(self.prefs["port"]) or prefs.DEFAULT_PORT)
        port = prefs.DEFAULT_PORT
        if not self.receiver:
            self.server = server.Server(port, self.do_action, self.set_hosts)
        else:
            self.server = server.Server(port, self.do_action)
        self.reset_menu(True)

    def reset_menu(self, initial=False):
        self.app.menu.clear()
        items = []
        if not self.receiver:
            if not self.listener.IS_TRUSTED:
                items.append(
                    rumps.MenuItem(
                        "Input Monitoring and Accessibility permissions are required."
                    )
                )
                items.append(rumps.MenuItem("Quit and reopen the app to try again."))
                items.append(rumps.separator)

        # build host menu
        host_menu = rumps.MenuItem("Hosts")
        if self.receiver:
            pass
        elif len(self.hosts_list) == 0:
            host_menu.add(rumps.MenuItem("No hosts"))
        else:
            for host in list(self.hosts_list):
                if host in self.prefs["hosts"]:
                    _host = rumps.MenuItem(f"{host} [{self.prefs['hosts'][host]}]")
                else:
                    _host = rumps.MenuItem(host)

                if self.prefs["hosts"].get(host) is not None:
                    _host.add(
                        rumps.MenuItem(
                            "Clear",
                            callback=self.set_host_key(host, self.prefs["hosts"][host]),
                        )
                    )
                    _host.add(rumps.separator)
                for k in pynput.keyboard.Key.__members__.keys():
                    key_item = rumps.MenuItem(k, callback=self.set_host_key(host, k))
                    if self.prefs["hosts"].get(host) == k:
                        key_item.state = True
                    _host.add(key_item)
                host_menu.add(_host)
        if not self.receiver:
            host_menu.add(rumps.separator)
            host_menu.add(rumps.MenuItem("Refresh", self.refresh_hosts))
            items.append(host_menu)

        # build action menu
        action_menu = rumps.MenuItem("Action")
        if self.prefs["action"] != "":
            action_menu.add(rumps.MenuItem(f"{self.prefs['action']}"))
            action_menu.add(rumps.separator)
            action_menu.add(rumps.MenuItem("Edit action...", callback=self.edit_action))
            action_menu.add(rumps.MenuItem("Clear", callback=self.clear_action))
        else:
            action_menu.add(rumps.MenuItem("No action"))
            action_menu.add(rumps.separator)
            action_menu.add(rumps.MenuItem("Set action...", callback=self.edit_action))

        items.append(action_menu)

        # build about menu
        items.append(
            rumps.MenuItem(
                "About",
                callback=lambda _: self.alert(
                    "Invoke a script on another Mac over LAN with a single keystroke.\n\n"
                ),
            )
        )

        # finally
        if not initial:
            items.append(rumps.MenuItem("Quit", callback=rumps.quit_application))
        self.app.menu = items

    def clear_action(self, _):
        self.prefs["action"] = ""
        self.save_prefs()
        self.reset_menu()

    def edit_action(self, _):
        action = osa(action_osa.format(self.prefs.get("action", "")))
        self.prefs["action"] = action
        self.save_prefs()
        self.reset_menu()

    # TODO: when the rumps version takes the top-level focus, use that
    def edit_action_rumps(self, _):
        action = rumps.Window(
            title="Edit Action",
            message=(
                "Enter the shell command to execute when another host presses the key they assigned to this host."
                "\n(Leave blank to be a send-only host)"
            ),
            default_text=self.prefs["action"],
            # cancel=True,
            ok="Save",
        ).run()
        if action.clicked:
            self.prefs["action"] = action.text
            self.save_prefs()
            self.reset_menu()

    def do_action(self, payload):
        if self.prefs["action"] == "":
            return
        # output = subprocess.check_output(
        subprocess.check_output(
            self.prefs["action"],
            shell=True,
            env={
                "LANKEY_FROM_HOST": payload["from"],
            },
        )
        # TODO: log this to a file that the user can open with another menu item
        # print("action output ---begin\n", output.decode(), "\n---end")

    def set_hosts(self, hosts):
        self.hosts_list = hosts

    def refresh_hosts(self, _):
        # the menu won't live update if it is open
        # so we pretend we're refreshing the list of hosts
        # but we're really just resetting the menu
        self.reset_menu()

    # returns a callback
    def set_host_key(self, host, key):
        def callback(_):
            if self.prefs["hosts"].get(host) == key:
                del self.prefs["hosts"][host]
            else:
                self.prefs["hosts"][host] = key
            self.save_prefs()
            self.reset_menu()

        return callback

    def alert(self, message):
        osa(message_osa.format(message))

    # TODO: when the rumps version takes the top-level focus, use that
    def alert_rumps(self, message):
        if not APP_RUN:
            self.alert(message)
        else:
            rumps.alert(
                title="LANKey",
                message=message,
            )

    def on_press(self, key: pynput.keyboard.KeyCode):
        key_value = "none"
        try:
            key_value = "{0}".format(key.char)
        except AttributeError:
            key_value = "{0}".format(key)

        self.reset_menu()
        for live_host in list(self.hosts_list):
            for host, host_key in self.prefs["hosts"].items():
                if live_host == host and key_value == f"Key.{host_key}":
                    # print(f"pressed {key_value} for {host}")
                    self.server.send(host)

    def run(self):
        self.server.start()
        if not self.receiver:
            self.listener.start()
            self.refresh_timer.start()
        self.app.run()


if __name__ == "__main__":
    LANKey().run()
