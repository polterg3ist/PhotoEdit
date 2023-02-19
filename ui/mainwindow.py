from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtGui import QPixmap, QImage
from base_ui.mainwindow_ui import Ui_MainWindow
from ui.settingwidget import SettingWidget
from PIL import Image, ImageFilter
from time import time
from ui.img_proc_thread import ImageProcThread


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.original = None

        self.new_image = None
        self.new_image_name = None
   
        self.img_proc_thread = None

        self.blur_setting = SettingWidget()
        self.blur_setting.ui.setting_name.setText("BLUR")

        self.unsharp_setting = SettingWidget()
        self.unsharp_setting.ui.setting_name.setText("UNSHARP")

        self.minimum_setting = SettingWidget()
        self.minimum_setting.ui.setting_name.setText("MINIMUM")
        self.minimum_setting.ui.horizontalSlider.setMaximum(10)
        self.minimum_setting.ui.horizontalSlider.setTickInterval(2)

        self.maximum_setting = SettingWidget()
        self.maximum_setting.ui.setting_name.setText("MAXIMUM")
        self.maximum_setting.ui.horizontalSlider.setMaximum(10)
        self.maximum_setting.ui.horizontalSlider.setTickInterval(2)

        self.filters = {self.blur_setting: ImageFilter.GaussianBlur,
                        self.unsharp_setting: ImageFilter.UnsharpMask,
                        self.minimum_setting: ImageFilter.MinFilter,
                        self.maximum_setting: ImageFilter.MaxFilter,
                        }

        self.rotates = {"actionRotate_90": Image.ROTATE_90,
                        "actionRotate_180": Image.ROTATE_180,
                        "actionFlip_left_to_right": Image.FLIP_LEFT_RIGHT,
                        }

        self.ui.actionOpen_a_file.triggered.connect(self.action_open_file)

    def rotate(self):
        action_name = self.sender().objectName()
        action = self.rotates[action_name]
        self.new_image_name = f"trash/{time()}.png"
        self.original = self.original.transpose(action)
        if self.new_image:
            self.slider_change()
        else:
            self.ui.label_Picture.setPixmap(self.pil2pixmap())

    def pil2pixmap(self):
        im2 = self.new_image.convert("RGBA")
        data = im2.tobytes("raw", "BGRA")
        qim = QImage(data, self.new_image.width, self.new_image.height, QImage.Format_ARGB32)
        pixmap = QPixmap.fromImage(qim)
        return pixmap

    def image_process(self):
        self.new_image = self.original.filter(ImageFilter.GaussianBlur(int(self.blur_setting.ui.setting_value.text())))
        for setting in (self.unsharp_setting, self.minimum_setting, self.maximum_setting):
            setting_value = int(setting.ui.setting_value.text())

            if setting_value != 0:
                if setting is not self.unsharp_setting and not setting_value % 2:
                    setting_value = setting_value - 1
                print(setting_value)
                self.new_image = self.new_image.filter(self.filters[setting](setting_value))

        self.ui.label_Picture.setPixmap(self.pil2pixmap())

    def start_editing(self):
        for setting in (self.blur_setting, self.unsharp_setting, self.minimum_setting, self.maximum_setting):
            self.ui.verticalLayout_2.addWidget(setting)
            setting.ui.horizontalSlider.valueChanged.connect(self.slider_change)
            setting.ui.horizontalSlider.sliderPressed.connect(self.sldDisconnect)
            setting.ui.horizontalSlider.sliderReleased.connect(self.sldReconnect)

        self.ui.actionRotate_90.triggered.connect(self.rotate)
        self.ui.actionRotate_180.triggered.connect(self.rotate)
        self.ui.actionFlip_left_to_right.triggered.connect(self.rotate)

        self.ui.actionSave_the_file.triggered.connect(self.action_save_file)

    def sldDisconnect(self):
        self.sender().valueChanged.disconnect()

    def sldReconnect(self):
        self.sender().valueChanged.connect(self.slider_change)
        self.sender().valueChanged.emit(self.sender().value())

    def slider_change(self):
        #print(self.sender())
        for setting in (self.blur_setting, self.unsharp_setting, self.minimum_setting, self.maximum_setting):
            setting.ui.setting_value.setText(str(setting.ui.horizontalSlider.value()))

        if self.img_proc_thread and self.img_proc_thread.is_alive():
            self.img_proc_thread.kill()
            self.img_proc_thread.join()
        self.img_proc_thread = ImageProcThread(target=self.image_process)
        self.img_proc_thread.start()

    def action_open_file(self):
        original_name = QFileDialog.getOpenFileName(filter=("*.png *.xpm *.jpg *.jpeg *.webp *.svg"))[0]
        self.original = Image.open(original_name)
        self.ui.label_Picture.setPixmap(QPixmap(original_name))
        self.start_editing()

    def action_save_file(self):
        try:
            opened_file = QFileDialog.getSaveFileName(self)[0]
            print(opened_file)
            if self.new_image:
                self.new_image.save(f"{opened_file}.png")
            else:
                self.original.save(f"{opened_file}.png")
        except Exception as er:
            print(er)