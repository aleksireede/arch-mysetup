from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton


def create_back_button(on_click):
    container = QFrame()
    container.setObjectName("backButtonCard")
    container.setFixedSize(150, 45)

    layout = QHBoxLayout(container)
    layout.setContentsMargins(10, 0, 10, 0)
    layout.setSpacing(5)
    layout.setAlignment(Qt.AlignCenter)

    back_btn = QPushButton("←")
    back_btn.setObjectName("backButtonArrow")
    back_lbl = QLabel("Back")
    back_lbl.setObjectName("backButtonLabel")

    layout.addWidget(back_btn)
    layout.addSpacing(20)
    layout.addWidget(back_lbl)
    layout.addStretch()

    container.mousePressEvent = lambda event: on_click()
    back_btn.clicked.connect(on_click)

    return container, back_btn, back_lbl, layout


def create_select_refresh_row(on_select_all, on_refresh):
    layout = QHBoxLayout()

    select_all_button = QPushButton("Select All")
    select_all_button.clicked.connect(on_select_all)

    refresh_button = QPushButton("Refresh")
    refresh_button.clicked.connect(on_refresh)

    layout.addWidget(select_all_button)
    layout.addStretch()
    layout.addWidget(refresh_button)

    return layout, select_all_button, refresh_button
