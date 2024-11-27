from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QCalendarWidget, QPushButton, QLineEdit, QDate, QListWidgetItem

class InputDialog(QDialog):
    def __init__(self, chapters):
        super().__init__()
        self.setWindowTitle('Input Dialog')
        self.setGeometry(100, 100, 400, 300)

        # max_days_map
        self.max_days_map = {'5m': 60-1, '15m': 60-1, '1h': 730-1, '1d': 3650}

        layout = QVBoxLayout()

        # Chapter Selection
        self.chapter_label = QLabel('Select the chapters:')
        self.chapter_list = QListWidget()
        self.chapter_list.setSelectionMode(QListWidget.MultiSelection)
        for chapter in chapters:
            item = QListWidgetItem(chapter)
            self.chapter_list.addItem(item)
        layout.addWidget(self.chapter_label)
        layout.addWidget(self.chapter_list)

        # Interval Selection
        self.interval_label = QLabel('Enter the interval (5m, 15m, 1h, 1d):')
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(['5m', '15m', '1h', '1d'])
        self.interval_combo.currentIndexChanged.connect(self.update_max_days)
        layout.addWidget(self.interval_label)
        layout.addWidget(self.interval_combo)

        # Plot Interval Selection
        self.plot_interval_label = QLabel('Enter the plot interval (5m, 15m, 1h, 1d):')
        self.plot_interval_combo = QComboBox()
        self.plot_interval_combo.addItems(['5m', '15m', '1h', '1d'])
        self.plot_interval_combo.currentIndexChanged.connect(self.update_max_days)
        layout.addWidget(self.plot_interval_label)
        layout.addWidget(self.plot_interval_combo)

        # Length of Simulation
        self.sim_length_label = QLabel('Enter the length of the simulation in days:')
        self.sim_length_input = QLineEdit()
        layout.addWidget(self.sim_length_label)
        layout.addWidget(self.sim_length_input)

        # Calendar for Start Date Selection
        self.start_date_label = QLabel('Select Start Date for Data:')
        self.start_date_calendar = QCalendarWidget()
        self.start_date_calendar.setGridVisible(True)
        self.start_date_calendar.setMaximumDate(QDate.currentDate())
        layout.addWidget(self.start_date_label)
        layout.addWidget(self.start_date_calendar)

        # Calendar for Plot Start Date Selection
        self.plot_start_date_label = QLabel('Select Plot Start Date:')
        self.plot_start_date_calendar = QCalendarWidget()
        self.plot_start_date_calendar.setGridVisible(True)
        self.plot_start_date_calendar.setMaximumDate(QDate.currentDate())
        layout.addWidget(self.plot_start_date_label)
        layout.addWidget(self.plot_start_date_calendar)

        # Submit Button
        self.submit_button = QPushButton('Submit')
        self.submit_button.clicked.connect(self.submit)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def update_max_days(self):
        interval = self.interval_combo.currentText()
        plot_interval = self.plot_interval_combo.currentText()

        if interval in self.max_days_map:
            max_days = self.max_days_map[interval]
            self.start_date_calendar.setMinimumDate(QDate.currentDate().addDays(-max_days))
        
        if plot_interval in self.max_days_map:
            max_days = self.max_days_map[plot_interval]
            self.plot_start_date_calendar.setMinimumDate(QDate.currentDate().addDays(-max_days))

    def submit(self):
        self.chapters = [item.text() for item in self.chapter_list.selectedItems()]
        self.interval = self.interval_combo.currentText()
        self.plot_interval = self.plot_interval_combo.currentText()
        self.sim_length = float(self.sim_length_input.text())
        self.start_date = self.start_date_calendar.selectedDate().toString('yyyy-MM-dd')
        self.plot_start_date = self.plot_start_date_calendar.selectedDate().toString('yyyy-MM-dd')

        self.accept()

#Example usage:
chapters = ['Chapter 1', 'Chapter 2', 'Chapter 3']
dialog = InputDialog(chapters)
if dialog.exec_() == QDialog.Accepted:
     print(f"Selected Chapters: {dialog.chapters}")
     print(f"Interval: {dialog.interval}")
     print(f"Plot Interval: {dialog.plot_interval}")
     print(f"Simulation Length: {dialog.sim_length}")
     print(f"Start Date: {dialog.start_date}")
     print(f"Plot Start Date: {dialog.plot_start_date}")
