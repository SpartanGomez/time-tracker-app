import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLineEdit, QLabel
from PyQt6.QtCore import QTimer, QTime, Qt
import sqlite3
from plyer import notification

class TimeTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Time Tracker")
        self.setGeometry(100, 100, 400, 500)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.project_input = QLineEdit()
        self.project_input.setPlaceholderText("Enter project name")
        self.layout.addWidget(self.project_input)

        self.add_project_button = QPushButton("Add Project")
        self.add_project_button.clicked.connect(self.add_project)
        self.layout.addWidget(self.add_project_button)

        self.project_list = QListWidget()
        self.layout.addWidget(self.project_list)

        self.time_label = QLabel("00:00:00")
        self.layout.addWidget(self.time_label)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_timer)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_timer)
        self.layout.addWidget(self.stop_button)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.time = QTime(0, 0, 0)

        self.init_db()

    def init_db(self):
        self.conn = sqlite3.connect('timetracker.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS projects
                              (id INTEGER PRIMARY KEY, name TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS time_entries
                              (id INTEGER PRIMARY KEY, project_id INTEGER, start_time TEXT, end_time TEXT)''')
        self.conn.commit()

    def add_project(self):
        project_name = self.project_input.text()
        if project_name:
            self.cursor.execute("INSERT INTO projects (name) VALUES (?)", (project_name,))
            self.conn.commit()
            self.project_list.addItem(project_name)
            self.project_input.clear()

    def start_timer(self):
        self.timer.start(1000)
        self.start_time = QTime.currentTime()

    def stop_timer(self):
        self.timer.stop()
        end_time = QTime.currentTime()
        project = self.project_list.currentItem()
        if project:
            project_name = project.text()
            self.cursor.execute("SELECT id FROM projects WHERE name = ?", (project_name,))
            project_id = self.cursor.fetchone()[0]
            self.cursor.execute("INSERT INTO time_entries (project_id, start_time, end_time) VALUES (?, ?, ?)",
                                (project_id, self.start_time.toString(Qt.DateFormat.ISODate),
                                 end_time.toString(Qt.DateFormat.ISODate)))
            self.conn.commit()

    def update_timer(self):
        self.time = self.time.addSecs(1)
        self.time_label.setText(self.time.toString("hh:mm:ss"))
        if self.time.second() % 300 == 0:  # Send notification every 5 minutes
            self.send_notification()

    def send_notification(self):
        notification.notify(
            title='Time Tracker',
            message='Stay focused! You\'ve been working for ' + self.time_label.text(),
            app_name='Time Tracker',
            timeout=10
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TimeTrackerApp()
    window.show()
    sys.exit(app.exec())