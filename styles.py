def get_menu_style():
    return """
        QMenuBar {
            background-color: #2e2e2e;
            color: #ffffff;
        }
        QMenuBar::item {
            background-color: #2e2e2e;
            color: #ffffff;
        }
        QMenuBar::item:selected {
            background-color: #111111;
        }
    """

def get_tab_style():
    return """
        QTabWidget::pane { /* The tab widget frame */
            border-top: 0.1px solid #C2C7CB;
            border: 1px #1e1e1e;
            background: #1e1e1e;
        }
        QTabBar::tab {
            height: 25px;
            min-height: 20px;
            max-height: 30px;
            background: #1e1e1e;
            color: grey;
            border: 1px solid black;
            padding: 10px;
            min-width: 80px;
        }
        QTabBar::tab:selected {
            background: #ffffff;
            color: black;
            border-bottom: none;
        }
        QTabBar::tab:hover {
            background: #ffffff;
        }
    """

def get_toolbar_style():
    return """
        QToolBar {
            background-color: #3c3f41;
        }
        QPushButton {
            background-color: #3a3a3a;
            color: #ffffff;
            border: 1px solid #555;
            padding: 5px 10px;
            margin-right: 5px;
        }
        QPushButton:hover {
            background-color: #111111;
        }
        QPushButton:pressed {
            background-color: #2c2c2c;
        }
    """
