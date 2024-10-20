import sys
import psutil
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, 
    QPushButton, QSystemTrayIcon, QMenu, QAction
)

class NetworkMonitorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.last_received = psutil.net_io_counters().bytes_recv
        self.last_sent = psutil.net_io_counters().bytes_sent
        self.initUI()

    def initUI(self):
        # Basic window setup

        self.setWindowTitle("Network Monitor")
        self.setFixedSize(200, 200)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create labels with larger font and white text
        self.download_label = QLabel("↓ 0.00 MB/s")
        self.upload_label = QLabel("↑ 0.00 MB/s")
        
        # Style labels
        label_style = """
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
            }
        """
        self.download_label.setStyleSheet(label_style)
        self.upload_label.setStyleSheet(label_style)
        
        # Add labels to layout
        layout.addWidget(self.download_label)
        layout.addWidget(self.upload_label)
        
        # Create control buttons
        buttons_layout = QVBoxLayout()
        self.close_button = QPushButton("×")
        self.minimize_button = QPushButton("−")
        
        # Style buttons
        button_style = """
            QPushButton {
                color: white;
                background: transparent;
                border: none;
                font-size: 16px;
                padding: 5px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 30);
            }
        """
        self.close_button.setStyleSheet(button_style)
        self.minimize_button.setStyleSheet(button_style)
        
        self.close_button.setFixedSize(20, 20)
        self.minimize_button.setFixedSize(20, 20)
        
        buttons_layout.addWidget(self.minimize_button)
        buttons_layout.addWidget(self.close_button)
        layout.addLayout(buttons_layout)
        
        # Set main layout
        self.setLayout(layout)
        
        # Style window
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 180);
                border-radius: 10px;
            }
        """)
        
        # Connect buttons
        self.close_button.clicked.connect(self.close)
        self.minimize_button.clicked.connect(self.showMinimized)
        
        # Setup system tray
        self.setup_tray()
        
        # Setup update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_network_stats)
        self.timer.start(1000)  # Update every second
        
        # Enable dragging
        self.oldPos = None

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        quit_action = QAction("Quit", self)
        
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(self.close)
        
        self.tray_menu.addAction(show_action)
        self.tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

    def update_network_stats(self):
        # Get current counters
        current = psutil.net_io_counters()
        
        # Calculate speeds
        download_speed = (current.bytes_recv - self.last_received) / 1024 / 1024  # MB/s
        upload_speed = (current.bytes_sent - self.last_sent) / 1024 / 1024  # MB/s
        
        # Update labels
        self.download_label.setText(f"↓ {download_speed:.2f} MB/s")
        self.upload_label.setText(f"↑ {upload_speed:.2f} MB/s")
        
        # Update last values
        self.last_received = current.bytes_recv
        self.last_sent = current.bytes_sent

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.oldPos:
            delta = event.globalPos() - self.oldPos
            self.move(self.pos() + delta)
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.oldPos = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create rounded rectangle background
        self.setWindowOpacity(0.6)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NetworkMonitorApp()
    window.show()
    sys.exit(app.exec_())