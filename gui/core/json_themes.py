# =============================================================================
# IMPORTS AND DEPENDENCIES
# =============================================================================
import json
import os

# =============================================================================
# SETTINGS IMPORT
# =============================================================================
from gui.core.json_settings import Settings

# =============================================================================
# THEME MANAGEMENT CLASS
# =============================================================================
class Themes(object):
    # =============================================================================
    # SETTINGS LOADING
    # =============================================================================
    setup_settings = Settings()
    _settings = setup_settings.items

    # =============================================================================
    # FILE PATH CONFIGURATION
    # =============================================================================
    json_file = f"gui/themes/{_settings['theme_name']}.json"
    app_path = os.path.abspath(os.getcwd())
    settings_path = os.path.normpath(os.path.join(app_path, json_file))
    if not os.path.isfile(settings_path):
        print(f"WARNING: \"gui/themes/{_settings['theme_name']}.json\" not found! check in the folder {settings_path}")

    # =============================================================================
    # INITIALIZATION
    # =============================================================================
    def __init__(self):
        super(Themes, self).__init__()

        self.items = {}

        self.deserialize()

    # =============================================================================
    # JSON SERIALIZATION METHODS
    # =============================================================================
    def serialize(self):
        with open(self.settings_path, "w", encoding='utf-8') as write:
            json.dump(self.items, write, indent=4)

    def deserialize(self):
        with open(self.settings_path, "r", encoding='utf-8') as reader:
            settings = json.loads(reader.read())
            self.items = settings