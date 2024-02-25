import os
import copy
import PySide6.QtCore as Qc
import PySide6.QtWidgets as Qw
import mainwindow as m

def strbool(i):
  if i == "1":
    return True
  elif i == "0":
    return False

class Option():
  def __init__(self,label:str,id:int):
    self.label = label
    self.id = id

Options = [Option('ニコニコモンズのみ表示',0),
          Option('フォルダのパスを表示',1),
          Option('ファイル名を表示',2),
          Option('(ニコニコモンズ限定)URLを表示',3),
          Option('同じフォルダに入っているファイルを表示しない',4),
          Option('特定のワードを含む物のみを表示',5),
          Option('ファイルを選択した状態で開く\n既存のエクスプローラーと別のプロセスで開かれます',6)
          ]

# データファイルが存在すれば読み込む
def load(data_file):
    evod = len(Options) % 2
    if os.path.isfile(data_file):
        data = []
        with open(data_file,'rb') as f:
            bt = f.read()
            for i in range(len(Options)):
                data.append(strbool(bt[:len(Options)//2 + evod].hex()[i+evod]))
            data.append(bt[len(Options)//2 + evod:].decode())
    else:
        data = [0]* len(Options)
        data.append("")
    return data

# 設定画面
class Config(Qw.QWidget):
  pathllist = []
  file = ""
  data_file = './data.dat'
  data = load(data_file)
  def __init__(self):
    super().__init__()
    Config.win = self
    sp_exp = Qw.QSizePolicy.Policy.Expanding
    # ウィンドウタイトル設定
    self.setWindowTitle('Config') 
    
    # ウィンドウのサイズ(300x250)と位置(X=200,Y=150)の設定
    self.setGeometry(300, 250, 200, 150)
    self.setMinimumSize(280,270)
    self.setMaximumSize(280,270)

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
    for opt in Options:
      cb = Qw.QCheckBox(self)
      if opt.id == 6:
        cb.setStyleSheet('color: #DE5065; font-weight: bold;')
      cb.setText(f'【{opt.label}】')
      cb.setCursor(Qc.Qt.CursorShape.PointingHandCursor)
      cb.Option = opt
      self.checkboxes.append(cb)
      main_layout.addWidget(cb)
      if self.data[opt.id]:
        cb.setCheckState(Qc.Qt.CheckState.Checked)
      if opt.id == 1:
        cb.stateChanged.connect(self.one_state_changed)
      elif opt.id == 2:
        cb.stateChanged.connect(self.two_state_changed)
      else:
        cb.stateChanged.connect(self.cb_state_changed)
      if opt.id == 5:
        # 入力フィールド
        self.tb_search = Qw.QLineEdit('',self)
        if not self.data[-1] == "":
          self.tb_search.setText(self.data[-1])
        self.tb_search.setPlaceholderText('絞り込む単語を入力')
        self.tb_search.setMinimumSize(10,10)
        self.tb_search.setSizePolicy(sp_exp,sp_exp)
        self.tb_search.setAcceptDrops(False)
        self.tb_search.editingFinished.connect(self.txt_changed)
        main_layout.addWidget(self.tb_search)

    # 保存ボタン
    self.btn_save = Qw.QPushButton('設定を保存')
    self.btn_save.setMinimumSize(50,20)
    self.btn_save.setMaximumSize(100,20)
    self.btn_save.setSizePolicy(sp_exp,sp_exp)
    button_layout.addWidget(self.btn_save)
    self.btn_save.clicked.connect(self.btn_save_clicked)

  def cb_state_changed(self):
    for i in range(len(self.checkboxes)):
      self.data[i] = self.checkboxes[i].isChecked()
    self.mainfunc()
  
  def one_state_changed(self):
    if self.checkboxes[1].isChecked():
        self.checkboxes[2].setCheckState(Qc.Qt.CheckState.Unchecked)
    self.cb_state_changed()

  def two_state_changed(self):
    if self.checkboxes[2].isChecked():
        self.checkboxes[1].setCheckState(Qc.Qt.CheckState.Unchecked)
    self.cb_state_changed()
    
  def txt_changed(self):
    self.data[-1]  = self.tb_search.text()
    self.mainfunc()
  
  def mainfunc(self):
    b = copy.deepcopy(self.pathllist)
    if not b == []:
      m.MainWindow.output(m.MainWindow.win,b,self.file)
    return
  
  def btn_save_clicked(self):
    a = 0
    for i in range(len(self.data)-1):
      if self.data[i]:
        a = a + 16 ** (len(self.data) -2 -i)
    with open(self.data_file,'wb') as file:
      file.write(a.to_bytes(len(Options)//2 + len(Options) % 2,"big")+self.data[-1].encode())