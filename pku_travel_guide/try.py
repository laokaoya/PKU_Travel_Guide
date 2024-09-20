
# 创建主窗口（旅游问卷GUI界面）
class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle(f"{username}{self.tr("的旅游问卷")}")
        self.username = username
        screen = QDesktopWidget()
        screen_geometry = screen.availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # 设置窗口的初始大小为屏幕大小
        self.setGeometry(0, 0, screen_width, screen_height-30)

        central_widget = QWidget(self)
        main_layout = QHBoxLayout(central_widget)

        left_widget = QWidget(central_widget)
        left_layout = QVBoxLayout(left_widget)
        left_widget.setFixedWidth(400)

        right_widget = QWidget(central_widget)
        right_layout = QVBoxLayout(right_widget)

        option_widgets = {}

        options = {
            self.tr("请选择您的计划游玩时间："): [self.tr("1小时以内"), self.tr("1-2小时"), self.tr("2-3小时"), self.tr("3-5小时"), self.tr("5小时以上")],
            self.tr("以下表述哪些符合您的游玩目的："): [self.tr("感受学术氛围与文化熏陶"), self.tr("了解名校往事与名人光辉"), self.tr("探寻历史遗迹与文物故事"), self.tr("欣赏山水自然与亭台楼榭"), self.tr("最高学府打卡并美美拍照")],
            self.tr("请选择您期望的游玩类型："): [self.tr("经典路线"), self.tr("小众景点"), self.tr("带娃出游"), self.tr("休闲不累"), self.tr("趣味活动")],
            self.tr("趣味活动："): [self.tr("燕园古树地图"), self.tr("燕园动物在哪里"), self.tr("隐秘的角落"), self.tr("燕园奇石与雕塑"), self.tr("校内食堂打卡")],
            self.tr("请列举您必去的景点（逗号分割）"): "", 
            self.tr("起始点："): read_start_locations(),
            self.tr("结束点："): read_end_locations()
        }

        activity_label = QLabel(self.tr("趣味活动："))
        activity_list_widget = QListWidget()
        activity_list_widget.setMinimumHeight(150)
        activity_list_widget.setSelectionMode(QListWidget.SingleSelection)
        for activity in options[self.tr("趣味活动：")]:
            activity_list_widget.addItem(activity)
        activity_label.setVisible(False)
        activity_list_widget.setVisible(False)

        for label_text, options_list in options.items():
            if label_text !="趣味活动：":
                label = QLabel(label_text)
                left_layout.addWidget(label)

            if label_text == self.tr("以下表述哪些符合您的游玩目的："):
                list_widget = QListWidget()
                list_widget.setMinimumHeight(150)
                list_widget.setSelectionMode(QListWidget.MultiSelection)
                for option in options_list:
                    list_widget.addItem(option)
                left_layout.addWidget(list_widget)
                option_widgets[label_text] = list_widget

            elif label_text == "请选择您期望的游玩类型：":
                combo_box = QComboBox()
                for option in options_list:
                    combo_box.addItem(option)
                left_layout.addWidget(combo_box)
                option_widgets[label_text] = combo_box
                combo_box.currentTextChanged.connect(lambda text: self.toggle_activity_visibility(text, activity_label, activity_list_widget))

            elif label_text == "请列举您必去的景点（逗号分割）":
                line_edit = QLineEdit()
                left_layout.addWidget(line_edit)
                option_widgets[label_text] = line_edit

            else:
                if label_text != "趣味活动：":
                    combo_box = QComboBox()
                    for option in options_list:
                        combo_box.addItem(option)
                    left_layout.addWidget(combo_box)
                    option_widgets[label_text] = combo_box

        left_layout.addWidget(activity_label)
        left_layout.addWidget(activity_list_widget)

        confirm_button = QPushButton("确定")
        confirm_button.clicked.connect(lambda: confirm_options(option_widgets, right_layout, right_widget))
        left_layout.addWidget(confirm_button)

        main_layout.addWidget(left_widget)

        initial_map_view = QWebEngineView()
        initial_map_view.load(QUrl.fromLocalFile(os.path.abspath("../map/pku_cluster_map.html")))
        initial_map_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(initial_map_view)

        right_widget.setLayout(right_layout)
        main_layout.addWidget(right_widget)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def toggle_activity_visibility(self, selected_text, activity_label, activity_list_widget):
        if selected_text == "趣味活动":
            activity_label.setVisible(True)
            activity_list_widget.setVisible(True)
        else:
            activity_label.setVisible(False)
            activity_list_widget.setVisible(False)

def create_gui():
    app = QApplication(sys.argv)
    welcome_window = WelcomeWindow()
    welcome_window.show()
    sys.exit(app.exec_())

create_gui()