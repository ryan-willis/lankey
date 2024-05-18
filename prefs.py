import json
import pathlib

DEFAULT_PORT = 6169
DEFAULT_PREFS = {"mode": "", "port": str(DEFAULT_PORT), "hosts": {}, "action": ""}
PREF_KEYS = list(DEFAULT_PREFS.keys())


class Prefs:
    _pref_file = pathlib.Path.home() / ".lankey"

    def write_pref(self, key, value):
        self.prefs[key] = value
        self.save_prefs()

    def save_prefs(self):
        self._pref_file.write_text(json.dumps(self.prefs))

    def load_prefs(self):
        if not self._pref_file.exists():
            self._pref_file.write_text(json.dumps(DEFAULT_PREFS))
        prefs_raw = self._pref_file.read_text()
        prefs = json.loads(prefs_raw)
        for key in PREF_KEYS:
            if key not in prefs or not isinstance(prefs[key], type(DEFAULT_PREFS[key])):
                print(f"key {key} not in prefs or not correct type")
                prefs[key] = DEFAULT_PREFS[key]

        self.prefs = prefs
