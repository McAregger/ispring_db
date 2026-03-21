from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QPushButton, QApplication, QVBoxLayout
import sys


class TestWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.test_button = PushButton()
        layout = QVBoxLayout(self)
        layout.addWidget(self.test_button)

        # connect Signal to to instance of where Signal is created
        self.test_button.test_signal.connect(self.do_it)

    #Slot --> callback function of test_signal
    def do_it(self, test_param):
        print(test_param[1])


class PushButton(QPushButton):
    # create Signal
    test_signal = Signal(tuple)
    def __init__(self):
        super().__init__()
        self.setText("Test")

        self.clicked.connect(self.test)

    def test(self):
        #fire Signal -> when fired connected Slot (callback function) will execute
        self.test_signal.emit(("Test", 25))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())


