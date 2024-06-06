import sys
import psycopg2
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QComboBox, QLabel, QListWidget, QMessageBox, \
    QGridLayout, QFrame, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView


class MilestoneApp(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Milestone - 1')

        main_layout = QGridLayout()

        # Add the title label and make it look official.
        self.title_label = QLabel('Milestone 1 - Page 1')
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
                    QLabel {
                        font-size: 24px;
                        font-weight: bold;
                        font-family: mono;
                        color: #333333;
                        padding: 10px;
                        margin: 10px;
                    }
                """)
        main_layout.addWidget(self.title_label, 0, 0)

        # Add the distinct states.
        self.distinct_states_label = QLabel('State')
        self.distinct_states_combo = QComboBox()
        states_container = self.container(self.distinct_states_label, self.distinct_states_combo)
        main_layout.addWidget(states_container, 1, 0)

        # Add the cities.
        self.cities_label = QLabel('Cities: ')
        self.cities_list = QListWidget()
        cities_container = self.container(self.cities_label, self.cities_list)
        main_layout.addWidget(cities_container, 2, 0)

        # Add the business table.
        self.add_business_table(main_layout)

        self.setLayout(main_layout)

        # Connect to the database.
        self.connect_db()

        # Update components to populate with values.
        self.update_state_combo()
        self.update_city_list()

        # Register listeners to the states combobox and the cities list.
        self.distinct_states_combo.currentIndexChanged.connect(self.update_city_list)
        self.cities_list.itemClicked.connect(self.update_business_table)

    def add_business_table(self, main_layout):
        # Add the business table.
        self.business_label = QLabel('Business: ')
        self.business_table = QTableWidget()

        # Set number of columns in the table.
        self.business_table.setColumnCount(3)

        # Set the width of the city and state column.
        self.business_table.setColumnWidth(1, 200)
        self.business_table.setColumnWidth(2, 100)

        # Stretch the business name column to accommodate the space on the page.
        business_header = self.business_table.horizontalHeader()
        business_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        # We don't want to see the column and row numbers.
        self.business_table.horizontalHeader().setVisible(False)
        self.business_table.verticalHeader().setVisible(False)

        # Create a new container for this item.
        business_container = self.container(self.business_label, self.business_table)

        # Add the widget to the main layout.
        main_layout.addWidget(business_container, 3, 0)

    # Connect to the PostgreSQL database.
    def connect_db(self):
        try:
            self.conn = psycopg2.connect(
                host='localhost',
                dbname='milestone1db',
                user='postgres',
                password='',
                port=5432
            )
        except Exception as e:
            QMessageBox.critical(self, 'Could not connect to the database:', str(e))

    def update_state_combo(self):
        if self.conn is None:
            QMessageBox.warning(self, 'Warning', "Could not connect to the database.")

        try:
            # Execute the command: SELECT DISTINCT state FROM business;
            cursor = self.conn.cursor()
            cursor.execute('select distinct state from business;')
            distinct_states = cursor.fetchall()
            cursor.close()

            # Populate the state combo box.
            for state in distinct_states:
                self.distinct_states_combo.addItems(state)

            self.business_table.clear()

        except Exception as e:
            QMessageBox.warning(self, 'Warning:', str(e))

    def update_city_list(self):
        # Clear the list of cities every time a state is changed.
        self.cities_list.clear()

        if self.conn is None:
            QMessageBox.warning(self, 'Warning', "Could not connect to the database.")

        # Get the current state selected.
        current_state = self.distinct_states_combo.currentText()

        try:
            cursor = self.conn.cursor()

            # Execute the command: SELECT DISTINCT city FROM business WHERE state=[selected state] ORDER BY city
            cursor.execute('select distinct city from business where state=%s order by city;', (current_state,))

            # Get the cities from the cursor.
            cities = cursor.fetchall()
            cursor.close()

            # Update the cities in the list.
            for city in cities:
                self.cities_list.addItems(city)

            # We want to clear the business table otherwise it won't match the current state and city.
            self.business_table.setRowCount(0)
            self.business_table.clear()

        except Exception as e:
            QMessageBox.warning(self, 'Warning:', str(e))

    def update_business_table(self):
        # We want to set the row count to zero as the clear function doesn't clear all the rows from the table.
        self.business_table.setRowCount(0)

        if self.conn is None:
            QMessageBox.warning(self, 'Warning', "Could not connect to the database.")

        # Get the current city and state.
        current_state = self.distinct_states_combo.currentText()
        current_city = self.cities_list.currentItem().text()

        try:
            cursor = self.conn.cursor()
            # Execute the command: SELECT name, state, city FROM business WHERE state=[select state] AND city=[select city] ORDER BY name;
            cursor.execute('select name, state, city from business where state=%s and city=%s order by name;', (current_state, current_city))
            businesses = cursor.fetchall()

            # There are a lot of values being updated here. It follows we don't want to display all these changes.
            self.business_table.setUpdatesEnabled(False)
            for business in businesses:
                self.add_business(business)

            # Re-enable updates in the business table to show the changes.
            self.business_table.setUpdatesEnabled(True)

        except Exception as e:
            QMessageBox.warning(self, 'Warning:', str(e))

    def add_business(self, business):
        # The sql command returns a list of tuples, that is, (name,state,city).
        name, state, city = business
        current_row = self.business_table.rowCount()
        # Create a new row at the last index and insert appropriate values.
        self.business_table.insertRow(current_row)
        self.business_table.setItem(current_row, 0, QTableWidgetItem(name))
        self.business_table.setItem(current_row, 1, QTableWidgetItem(city))
        self.business_table.setItem(current_row, 2, QTableWidgetItem(state))

    # Create styled containers.
    def container(self, component_label, component):
        bg = QFrame(self)

        # Add Style
        bg.setStyleSheet(f"""
            QFrame {{
                background-color: #f0f0f0 ;
                border: 1px solid #d1d1d1;
                border-radius: 1px;      
                padding: 6px;           
                margin: 6px;           
            }}
            
            QLabel {{
                font-size: 16px;
                color: #333333;
            }}
            
            QListWidget {{
                border-radius: 1px;
                border: 1px solid #ccc;
                padding: 5px;
                background-color: white;
            }}
            
            QComboBox {{
                background-color: white;
                border: 1px solid black;
                padding: 5px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: white;
                selection-background-color: lightgray;
                selection-color: black;
            }}
            
            QComboBox:hover {{
                background-color: lightgray;
            }}
        """)

        layout = QVBoxLayout()
        if component_label is not None:
            layout.addWidget(component_label)

        if component is not None:
            layout.addWidget(component)

        bg.setLayout(layout)

        return bg


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MilestoneApp()
    ex.show()
    sys.exit(app.exec())
