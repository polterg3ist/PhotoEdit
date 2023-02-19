from base_ui.settingwidget_ui import Ui_SettingsWidget
from PyQt5.QtWidgets import QWidget


class SettingWidget(QWidget):
    def __init__(self):
        super(SettingWidget, self).__init__()
        self.ui = Ui_SettingsWidget()
        self.ui.setupUi(self)