import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QCalendarWidget
from PyQt5.QtCore import QDate
from GBM_Simulations import GBMS

class InputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Input Dialog')
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        # Ticker Symbol
        self.ticker_label = QLabel('Enter the ticker symbol:')
        self.ticker_input = QLineEdit()
        layout.addWidget(self.ticker_label)
        layout.addWidget(self.ticker_input)

        # Interval Selection
        self.interval_label = QLabel('Enter the interval (5m, 15m, 1h, 1d):')
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(['5m', '15m', '1h', '1d'])
        layout.addWidget(self.interval_label)
        layout.addWidget(self.interval_combo)

        # Plot Interval Selection
        self.plot_interval_label = QLabel('Enter the plot interval (5m, 15m, 1h, 1d):')
        self.plot_interval_combo = QComboBox()
        self.plot_interval_combo.addItems(['5m', '15m', '1h', '1d'])
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

    def submit(self):
        self.ticker = self.ticker_input.text()
        self.interval = self.interval_combo.currentText()
        self.plot_interval = self.plot_interval_combo.currentText()
        self.sim_length = float(self.sim_length_input.text())
        self.start_date = self.start_date_calendar.selectedDate().toString('yyyy-MM-dd')
        self.plot_start_date = self.plot_start_date_calendar.selectedDate().toString('yyyy-MM-dd')

        self.accept()

def main():
    app = QApplication(sys.argv)
    dialog = InputDialog()
    if dialog.exec() == QDialog.Accepted:
        # Access input parameters after the dialog is accepted
        ticker = dialog.ticker
        interval = dialog.interval
        plot_interval = dialog.plot_interval
        sim_length = dialog.sim_length
        start_date = dialog.start_date
        plot_start_date = dialog.plot_start_date

        print(f'Ticker: {ticker}')
        print(f'Interval: {interval}')
        print(f'Plot Interval: {plot_interval}')
        print(f'Simulation Length (days): {sim_length}')
        print(f'Start Date: {start_date}')
        print(f'Plot Start Date: {plot_start_date}')

        # Use the variables in your main code
        # For example:
        GBMS(ticker, interval, plot_interval, sim_length, start_date, plot_start_date)

if __name__ == '__main__':
    main()
