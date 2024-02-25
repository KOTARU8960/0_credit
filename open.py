import os
import copy
import PySide6.QtCore as Qc
import PySide6.QtWidgets as Qw
import webbrowser
import mainwindow as m
import subprocess
import config as c

# ジャンプ画面
class Open(Qw.QScrollArea):
  def __init__(self):
    #region
    self.sortresult = copy.deepcopy(m.MainWindow.win.sortresult)
    if not c.Config.data[6]:
      folders:list = []
      gm:list = []
      for i in range(len(self.sortresult)):
          if self.sortresult[i][0:8] == "https://":
              continue
          eb = self.sortresult[i].rfind("\\")
          sb = self.sortresult[i].rfind("\\",0,eb)
          folder = self.sortresult[i][sb:eb]
          if folder in folders:
              gm.append(i)
          folders.append(folder)
      for i in range(len(gm)):
          self.sortresult.pop(gm[i]-i)
      self.sortresult = [i if i.startswith("https://") else i[:i.rfind('\\')] for i in self.sortresult]
    #endregion
    super().__init__()
    Open.win = self
    sp_exp = Qw.QSizePolicy.Policy.Expanding
    # ウィンドウタイトル設定
    self.setWindowTitle('ソースを表示する') 

    # ウィンドウのサイズ(800x200)と位置(X=100,Y=400)の設定
    self.setGeometry(100, 400, 800, 200)
    self.setMinimumSize(300,200)

    # メインレイアウトの設定
    central_widget = Qw.QWidget(self)
    main_layout = Qw.QVBoxLayout(central_widget) # 要素を垂直配置
    main_layout.setAlignment(Qc.Qt.AlignmentFlag.AlignTop) # 上寄せ
    main_layout.setContentsMargins(15,10,10,10)
    button_layout = Qw.QHBoxLayout()
    button_layout.setAlignment(Qc.Qt.AlignmentFlag.AlignLeft) # 左寄せ
    main_layout.addLayout(button_layout) # メインレイアウトにボタンレイアウトを追加

    # チェックボックスの生成と設定
    self.checkboxes : list[Qw.QCheckBox] = []
    for i in self.sortresult:
      cb = Qw.QCheckBox(self)
      cb.setText(i)
      cb.setCursor(Qc.Qt.CursorShape.PointingHandCursor)
      self.checkboxes.append(cb)
      main_layout.addWidget(cb)
      cb.setCheckState(Qc.Qt.CheckState.Checked)

    #「Open」ボタンの生成と設定
    self.btn_open = Qw.QPushButton('Open')
    self.btn_open.setMinimumSize(50,20)
    self.btn_open.setMaximumSize(100,20)
    self.btn_open.setSizePolicy(sp_exp,sp_exp)
    button_layout.addWidget(self.btn_open)
    self.btn_open.clicked.connect(self.btn_open_clicked)

    #「全選択」ボタンの生成と設定
    self.btn_all = Qw.QPushButton('全選択')
    self.btn_all.setMinimumSize(50,20)
    self.btn_all.setMaximumSize(100,20)
    self.btn_all.setSizePolicy(sp_exp,sp_exp)
    button_layout.addWidget(self.btn_all)
    self.btn_all.clicked.connect(self.btn_all_clicked)

    #「全選択解除」ボタンの生成と設定
    self.btn_notall = Qw.QPushButton('全選択解除')
    self.btn_notall.setMinimumSize(50,20)
    self.btn_notall.setMaximumSize(100,20)
    self.btn_notall.setSizePolicy(sp_exp,sp_exp)
    button_layout.addWidget(self.btn_notall)
    self.btn_notall.clicked.connect(self.btn_notall_clicked)

    inner = central_widget
    layout = main_layout
    inner.setLayout(layout)
    self.setWidget(inner)

  def btn_open_clicked(self):
    for i in range(len(self.checkboxes)):
      if self.checkboxes[i].isChecked():
        if self.sortresult[i].startswith("https://"):
          webbrowser.open(self.sortresult[i], new=0, autoraise=True)
        elif os.path.isfile(self.sortresult[i]) and c.Config.data[6]:
          subprocess.Popen(['explorer', r"/select,"+ m.MainWindow.win.sortresult[i]], shell=False)
        elif os.path.isdir(self.sortresult[i]) and not c.Config.data[6]:
          os.startfile(self.sortresult[i])
    m.MainWindow.win.lb_navi.setText(f"エクスプローラー、ブラウザで表示しました")
    self.close()

  def btn_all_clicked(self):
    for i in self.checkboxes:
      i.setCheckState(Qc.Qt.CheckState.Checked)

  def btn_notall_clicked(self):
    for i in self.checkboxes:
      i.setCheckState(Qc.Qt.CheckState.Unchecked)