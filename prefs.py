import json
import pathlib

DEFAULT_PORT = 6169
DEFAULT_PREFS = {"mode": "", "port": str(DEFAULT_PORT), "action": "", "hosts_v2": {}}
PREF_KEYS = list(DEFAULT_PREFS.keys())


class Prefs:
    _pref_file = pathlib.Path.home() / ".lankey"

    def save_prefs(self):
        for host in self.prefs["hosts_v2"]:
            if host not in self.prefs.get("hosts", {}):
                continue
            if len(self.prefs["hosts_v2"][host]) == 0:
                del self.prefs["hosts"][host]
            else:
                self.prefs["hosts"][host] = self.prefs["hosts_v2"][host][0]
        self._pref_file.write_text(json.dumps(self.prefs))

    def load_prefs(self):
        if not self._pref_file.exists():
            self._pref_file.write_text(json.dumps(DEFAULT_PREFS))
        prefs_raw = self._pref_file.read_text()
        prefs = json.loads(prefs_raw)

        # migrate the old prefs to the new format
        if "hosts_v2" not in prefs and "hosts" in prefs:
            prefs["hosts_v2"] = {}
            for host in prefs["hosts"]:
                prefs["hosts_v2"][host] = [prefs["hosts"][host]]

        for key in PREF_KEYS:
            if key not in prefs or not isinstance(prefs[key], type(DEFAULT_PREFS[key])):
                print(f"key {key} not in prefs or not correct type")
                prefs[key] = DEFAULT_PREFS[key]

        self.prefs = prefs
