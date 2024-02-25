import sys
import PySide6.QtWidgets as Qw
import mainwindow as m

# 本体
if __name__ == '__main__':
  app = Qw.QApplication(sys.argv)
  main_window = m.MainWindow()
  main_window.show()
  sys.exit(app.exec())