import os
import re
import copy
import PySide6.QtCore as Qc
import PySide6.QtWidgets as Qw
import chardet
import config as c
import open as o

alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

pickdata = [b"\x00",b"\x2f",b"\x2a",b"\x3f",b"\x22",b"\x3c",b"\x3e",b"\x7c",b"\x3a",b"\x0D"]

# PySide6.QtWidgets.MainWindow を継承した MainWindow クラスの定義
class MainWindow(Qw.QMainWindow):
  sortresult:list
  def __init__(self):
    super().__init__()
    MainWindow.win = self
    sp_exp = Qw.QSizePolicy.Policy.Expanding

    self.setAcceptDrops(True)

    # ウィンドウタイトル設定
    self.setWindowTitle('クレジット確認') 

    # ウィンドウのサイズ(640x240)と位置(X=100,Y=50)の設定
    self.setGeometry(100, 50, 640, 240)
    self.setMinimumSize(320,200) 

    central_widget = Qw.QWidget(self)
    self.setCentralWidget(central_widget)
    main_layout = Qw.QVBoxLayout(central_widget) # 要素を垂直配置
    main_layout.setAlignment(Qc.Qt.AlignmentFlag.AlignTop) # 上寄せ
    main_layout.setContentsMargins(15,10,10,10)
    button_layout = Qw.QHBoxLayout()
    button_layout.setAlignment(Qc.Qt.AlignmentFlag.AlignLeft) # 左寄せ
    main_layout.addLayout(button_layout) # メインレイアウトにボタンレイアウトを追加

    #「Open」ボタンの生成と設定
    self.btn_open = Qw.QPushButton('Open')
    self.btn_open.setMinimumSize(50,20)
    self.btn_open.setMaximumSize(100,20)
    self.btn_open.setSizePolicy(sp_exp,sp_exp)
    button_layout.addWidget(self.btn_open)
    self.btn_open.clicked.connect(self.btn_open_clicked)

    #「Setting」ボタンの生成と設定
    self.btn_setting = Qw.QPushButton('設定')
    self.btn_setting.setMinimumSize(50,20)
    self.btn_setting.setMaximumSize(100,20)
    self.btn_setting.setSizePolicy(sp_exp,sp_exp)
    button_layout.addWidget(self.btn_setting)
    self.btn_setting.clicked.connect(self.btn_setting_clicked)

    #「.txt出力」ボタンの生成と設定
    self.btn_file = Qw.QPushButton('.txt出力')
    self.btn_file.setMinimumSize(50,20)
    self.btn_file.setMaximumSize(100,20)
    self.btn_file.setSizePolicy(sp_exp,sp_exp)
    self.btn_file.setEnabled(False)
    button_layout.addWidget(self.btn_file)
    self.btn_file.clicked.connect(self.btn_file_clicked)

    #「フォルダを開く」ボタンの生成と設定
    self.btn_source = Qw.QPushButton('フォルダ、URLを開く')
    self.btn_source.setMinimumSize(50,20)
    self.btn_source.setMaximumSize(100,20)
    self.btn_source.setSizePolicy(sp_exp,sp_exp)
    self.btn_source.setEnabled(False)
    button_layout.addWidget(self.btn_source)
    self.btn_source.clicked.connect(self.btn_source_clicked)

    # ナビゲーション情報を表示するラベル
    self.init_navi_msg = \
      '[Open] ボタンを押下してファイルを選択するかドラッグアンドドロップ'
    self.lb_navi = Qw.QLabel(self.init_navi_msg,self)
    self.lb_navi.setMinimumSize(100,15)
    self.lb_navi.setSizePolicy(sp_exp,sp_exp)
    main_layout.addWidget(self.lb_navi)

    # テキストボックス
    self.tb_viwer = Qw.QTextEdit('',self)
    self.tb_viwer.setPlaceholderText('(読み込んだファイルの内容が表示されます)')
    self.tb_viwer.setMinimumSize(20,100)
    self.tb_viwer.setSizePolicy(sp_exp,sp_exp)
    self.tb_viwer.setAcceptDrops(False)
    self.tb_viwer.setReadOnly(True)
    main_layout.addWidget(self.tb_viwer)

  # settingウィンドウ
  def btn_setting_clicked(self):
    self.w = c.Config()
    self.w.show()
      
  # txt出力
  def btn_file_clicked(self):
    txt = self.tb_viwer.toPlainText()
    if len(txt) == 0:
      return
    title = 'ファイルの保存' 
    default_path = os.path.expanduser("./" + txt[:txt.find("\n")])
    filter = 'Text file (*.txt)'
    path = Qw.QFileDialog.getSaveFileName(
            self,         # 親ウィンドウ
            title,        # ダイアログタイトル
            default_path, # デフォルトファイル名
            filter)       # 拡張子によるフィルタ

    if path[0] == '' :
      self.lb_navi.setText('保存をキャンセルしました。')
      return

    self.save_text(path[0],txt)
    self.lb_navi.setText(f"ログを '{path[0]}' に保存しました。")

  # エクスプローラーで表示
  def btn_source_clicked(self):
    self.w = o.Open()
    self.w.show()
    

  # テキストモードでファイルの書き込み
  def save_text(self,path,text):
    with open(path, mode='w', encoding='utf_8') as file:
      text = file.write(text)

  #「Open」ボタンの押下処理
  def btn_open_clicked(self):
    title = ''
    init_path = os.path.expanduser('~/Documents')
    path = Qw.QFileDialog.getOpenFileName(
            self,      # 親ウィンドウ
            title,     # ダイアログタイトル
            init_path, # 初期位置（フォルダパス）
            )

    if path[0] == '' :
      self.lb_navi.setText(self.init_navi_msg)
      return
    
    self.read_text(path[0])

  # ドラッグ処理
  def dragEnterEvent(self,e):
    if(e.mimeData().hasUrls()):
      e.accept()

  # ドロップ処理
  def dropEvent(self, e):
    urls = e.mimeData().urls()
    url = urls[0]
    self.read_text(url.toLocalFile())

  # 終了処理
  def closeEvent(self,event):
    try:
      c.Config.win.close()
    except AttributeError:
      pass
    try:
      o.Open.win.close()
    except AttributeError:
      pass
    pass

  # バイナリモードでファイルの読込み
  def read_text(self,path):
    self.lb_navi.setText(f"ファイル '{path}' を読み込みました。")
    assert os.path.isfile(path) == True 
    with open(path, 'rb') as file:
      text = file.read()
    index = []
    credit = []
    for l in alpha:
      drive = l.encode()
      index.append(text.find(drive + b'\x3A\x5C'))
      while(True):
        if index[-1] == -1:
          index.pop(-1)
          break
        index.append(text.find(drive + b'\x3A\x5C',index[-1]+2))
    for i in range(len(index)):
      a = 0
      for l in pickdata:
        ind = text.find(l,index[i]+2)
        if not ind == -1 and (a > ind or a == 0):
          a = ind
      p = text[index[i]:a]
      if  b"\x2e" not in p:
        continue
      while(True):
        try:
          strp = p.decode(encoding=chardet.detect(p)["encoding"])
        except UnicodeDecodeError:
          p = p[:len(p)-1]
          continue
        if not strp == "":
          period = strp.rfind(".")+1
          exception = re.search(r'[^a-zA-Z1-9]', strp[period:])
          if exception:
            strp = strp[:exception.start()+period]
          credit.append(strp)
        break
      gm = [m.start() for m in re.finditer(r'\\\\', strp)]
      for l in range(len(gm)):
        credit[-1] = credit[-1][:gm[l]-l] + credit[-1][gm[l]-l+1:]
    credit = list(set(credit))
    c.Config.pathllist = copy.deepcopy(credit)
    c.Config.file = path[path.rfind('/')+1:]
    self.output(credit,path[path.rfind('/')+1:])
    return
  
  def output(self,credit,file):
    data = c.Config.data
    if data[0]:
      credit = [i for i in credit if re.search(r'nc[1234567890]', i)]
    if data[5]:
      credit = [i for i in credit if re.search(data[-1], i)]
    if data[3]:
      credit = ["https://commons.nicovideo.jp/works/" + i[i.rfind('nc'):i.rfind('.')] if re.search(r'nc[1234567890]', i) else i for i in credit]
    if data[4]:
      folders:list = []
      gm:list = []
      for i in range(len(credit)):
        eb = credit[i].rfind("\\")
        sb = credit[i].rfind("\\",0,eb)
        folder = credit[i][sb:eb]
        if folder in folders:
          gm.append(i)
        folders.append(folder)
      for i in range(len(gm)):
        credit.pop(gm[i]-i)
    self.sortresult = copy.deepcopy(credit)
    if data[1]:
      credit = [i if i.startswith("https://") else i[:i.rfind('\\')] for i in credit]
    if data[2]:
      credit = [i if i.startswith("https://") else i[i.rfind('\\')+1:] for i in credit]
    if len(credit) == 0 :
      self.btn_source.setEnabled(False)
      self.btn_file.setEnabled(False)
      self.tb_viwer.setPlainText("")
      self.tb_viwer.setPlaceholderText('対象が見つかりませんでした')
    else:
      self.btn_source.setEnabled(True)
      self.btn_file.setEnabled(True)
      self.tb_viwer.setPlainText(f"{file}内に記述のあるファイル\n" + '\n'.join(credit))


