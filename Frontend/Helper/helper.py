from sqlalchemy.orm import sessionmaker, class_mapper
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import sessionmaker
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from collections import defaultdict
import signal
import typing
# PyQt6
from functools import partial
import PyQt6
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import (
    QPixmap,
    QIcon,
    QColor
)
from PyQt6.QtWidgets import QWidget
import qrcode

from Backend.Database.db_sessions import *

""" Paths """
icon_search_path = "Frontend/Resources/Bootstrap/search.png"
icon_options_path = "Frontend/Resources/Bootstrap/sliders.png"
icon_home_path = "Frontend/Resources/Bootstrap/house-fill.png"
icon_back_path = "Frontend/Resources/Bootstrap/arrow-left.png"
icon_x_path = "Frontend/Resources/Bootstrap/x-lg.png"
icon_qr_code_path = "Frontend/Resources/Bootstrap/qr-code.png"
icon_refresh_path = "Frontend/Resources/Bootstrap/arrow-clockwise.png"

icon_menu_path = "Frontend/Resources/Bootstrap/list.png"
icon_show_path = "Frontend/Resources/Bootstrap/eye.png"
icon_hide_path = "Frontend/Resources/Bootstrap/eye-slash.png"
icon_edit_path = "Frontend/Resources/Bootstrap/pencil-square.png"
icon_delete_path = "Frontend/Resources/Bootstrap/trash3.png"


def clearAllWidgets(parent_widget: QWidget):
    parent_widget_layout = parent_widget.layout()
    if parent_widget_layout:
        clearAllWidgetOfLayout(parent_widget_layout)


def clearAllWidgetOfLayout(parent_layout: QLayout):
    while parent_layout.count():
        widget = parent_layout.takeAt(0).widget()
        if widget:
            widget.deleteLater()


"""
┌───────────────────────┐                                                       
│┌─────────────────────┐│  ┌────────────────────────┐                           
││      frame_Khu      ││  │┌──────────────────────┐│                           
│└─────────────────────┘│  ││     label_TenKhu     ││                           
│┌─────────────────────┐│  │└──────────────────────┘│                           
││      frame_Khu     ─┼┼─▶│┌──────────────────────┐│  ┌───────────────────────┐
│└─────────────────────┘│  ││                      ││  │ ┌─────┐┌─────┐┌─────┐ │
│┌─────────────────────┐│  ││     Frame_Phongs    ─┼┼─▶│ └─────┘└─────┘└─────┘ │
││      frame_Khu      ││  ││                      ││  │ ┌─────┐┌─────┐        │
│└─────────────────────┘│  │└──────────────────────┘│  │ └─────┘└─────┘        │
└───────────────────────┘  └────────────────────────┘  └───────────────────────┘
       Frame_Khus                  Frame_Khu                 Frame_Phongs       
"""


def setTableTextCell(table: QTableWidget, text: str, row, col):
    qitem = QTableWidgetItem(text)
    qitem.setFlags(qitem.flags() & ~PyQt6.QtCore.Qt.ItemFlag.ItemIsEditable)
    table.setItem(row, col, qitem)


def setTableWidgetCell(table: QTableWidget, widget: QWidget, row, col):
    table.setCellWidget(row, col, widget)


def setTableResizeMode(table: QTableWidget, resize_modes: List[QHeaderView.ResizeMode]):
    for col, resize_mode in enumerate(resize_modes):
        table.horizontalHeader().setSectionResizeMode(col, resize_mode)


class Frame_Phongs(QFrame):
    def __init__(self, parent: QWidget, phongs: List[Phong], callback_pushButton_Phong=None) -> None:
        super().__init__(parent)
        # Empty Khu with no phong
        if not phongs:
            self.layout = QVBoxLayout(self)
            self.layout.addWidget(QLabel("Không có phòng nào thuộc khu này!"))
            return
        # Grid layout for Phongs
        self.layout = QGridLayout(self)
        # Calculate rows and columns based on the number of Phongs
        len_phongs = len(phongs)
        rows = (len_phongs - 1) // 5 + 1
        columns = min(len_phongs, 5)

        for i, phong in enumerate(phongs):
            pushButton_Phong = QPushButton(parent=self,
                                           text=f'P.{phong.ma}')
            if callback_pushButton_Phong:
                pushButton_Phong.clicked.connect(
                    partial(callback_pushButton_Phong, phong=phong))
            # Calculate the row and column positions based on the index
            row_position = i // columns
            column_position = i % columns
            self.layout.addWidget(pushButton_Phong,
                                  row_position,
                                  column_position,
                                  1,
                                  1)


class Frame_Khu(QFrame):
    def __init__(self, parent: QWidget, khu: Khu, callback_pushButton_Phong=None) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        # Label for Khu
        label_TenKhu = QLabel(parent=self,
                              text=khu.ten)
        self.layout.addWidget(label_TenKhu)
        # Frame for Phongs in Khu
        frame_Phongs = Frame_Phongs(parent=self,
                                    phongs=khu.phongs,
                                    callback_pushButton_Phong=callback_pushButton_Phong)
        self.layout.addWidget(frame_Phongs)


class Frame_Khus(QFrame):
    def __init__(self, parent: QWidget, khus: List[Khu], callback_pushButton_Phong=None) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        for khu in khus:
            if not khu.phongs:
                continue
            frame_Khu = Frame_Khu(parent=self,
                                  khu=khu,
                                  callback_pushButton_Phong=callback_pushButton_Phong)
            self.layout.addWidget(frame_Khu)


class Frame_RoomInfo_Info(QFrame):
    def __init__(self, parent: QWidget, phong: Phong) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        label_texts = [
            f"Mã phòng: P.{phong.ma}",
            f"Tên phòng: {phong.ten}",
            f"Khu vực: {phong.khu.ten if phong.khu else ''}",
            f"Đơn vị quản lý: {phong.don_vi.ten if phong.don_vi else ''}",
            f"Cán bộ quản lý: {phong.can_bo.ten if phong.can_bo else ''}",
            f"SĐT liên hệ: {phong.can_bo.sdt if phong.can_bo.sdt else '' if phong.can_bo else ''}",
            f"Thông tin phòng: {phong.thong_tin if phong.thong_tin else ''}"
        ]
        for label_text in label_texts:
            label = QLabel(parent=self,
                           text=label_text)
            self.layout.addWidget(label)
        spacer_widget = QWidget(parent=self)
        spacer_widget.setSizePolicy(QSizePolicy.Policy.Expanding,
                                    QSizePolicy.Policy.Expanding)
        self.layout.addWidget(spacer_widget)


class Frame_RoomInfo_DanhMuc(QFrame):
    def __init__(self, parent: QWidget, phong: Phong) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self = QTableWidget(parent=self)


class Table_DanhMuc(QTableWidget):
    def __init__(self, parent: QWidget, phong: Phong, callback_DetailButton=None) -> None:
        super().__init__(parent)
        header_labels = [
            'STT',
            'Mã tài sản',
            'Loại tài sản',
            'SL',
            'Chức năng'
        ]
        resize_modes = [
            QHeaderView.ResizeMode.ResizeToContents,
            QHeaderView.ResizeMode.ResizeToContents,
            QHeaderView.ResizeMode.Stretch,
            QHeaderView.ResizeMode.ResizeToContents,
            QHeaderView.ResizeMode.ResizeToContents
        ]
        column_count = len(header_labels)
        self.setColumnCount(column_count)
        self.setHorizontalHeaderLabels(header_labels)
        setTableResizeMode(table=self,
                           resize_modes=resize_modes)
        # Fill table
        # Dictionary of dictionaries of lists of tai_san
        tai_sans_grouped = defaultdict(lambda: defaultdict(list))
        for tai_san in phong.tai_sans:
            loai_tai_san = tai_san.loai_tai_san if tai_san.loai_tai_san else None
            nhom_tai_san = loai_tai_san.nhom_tai_san if loai_tai_san else None
            if loai_tai_san and nhom_tai_san:
                tai_sans_grouped[nhom_tai_san][loai_tai_san].append(tai_san)
        # Number of row in table = total nhom tai san + total loai tai san
        row_count = len(tai_sans_grouped)
        for nhom_tai_san, loai_tai_san_list in tai_sans_grouped.items():
            row_count += len(loai_tai_san_list)
        self.setRowCount(row_count)
        # Display
        row = 0
        for nhom_tai_san, loai_tai_san_dict in tai_sans_grouped.items():
            # Nhom tai san
            # print(f"Nhom tai san: {nhom_tai_san.ten}")
            # Display ten Nhom Tai San
            self.setSpan(row, 0, 1, column_count)
            qitem_ten_danh_muc = QTableWidgetItem(nhom_tai_san.ten)
            qitem_ten_danh_muc.setFlags(
                qitem_ten_danh_muc.flags() & ~PyQt6.QtCore.Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 0, qitem_ten_danh_muc)
            row += 1
            stt = 1
            for loai_tai_san, tai_san_list in loai_tai_san_dict.items():
                # Loai tai san
                # print(f"    Loai tai san: {loai_tai_san.ten}")
                items = [
                    f"{stt}",
                    f"{phong.don_vi.ma}.{phong.ma}.{loai_tai_san.ma}",
                    loai_tai_san.ten,
                    f"{len(tai_san_list)}",
                ]
                for col, item in enumerate(items):
                    setTableTextCell(table=self,
                                     text=item if item else '',
                                     row=row,
                                     col=col)
                # chi tiet
                button_detail = QPushButton(text='Chi tiết',
                                            parent=self)
                button_detail.clicked.connect(partial(
                    callback_DetailButton, phong=phong, loai_tai_san=loai_tai_san, tai_san_list=tai_san_list))
                setTableWidgetCell(table=self,
                                   row=row,
                                   col=column_count - 1,
                                   widget=button_detail)

                row += 1
                stt += 1
        # Custom display for cols and rows of table
        self.resizeColumnsToContents()
        self.resizeRowsToContents()


class Table_DanhMuc_Detail(QTableWidget):
    def __init__(self, parent: QWidget, phong: Phong, loai_tai_san: LoaiTaiSan, tai_san_list: List[TaiSan]) -> None:
        super().__init__(parent)
        header_labels = [
            'STT',
            'Mã định danh tài sản',
            'Mô tả chi tiết tài sản',
            'Ghi chú'
        ]
        resize_modes = [
            QHeaderView.ResizeMode.ResizeToContents,
            QHeaderView.ResizeMode.ResizeToContents,
            QHeaderView.ResizeMode.Stretch,
            QHeaderView.ResizeMode.ResizeToContents
        ]
        column_count = len(header_labels)
        self.setColumnCount(column_count)
        self.setHorizontalHeaderLabels(header_labels)
        setTableResizeMode(table=self,
                           resize_modes=resize_modes)
        # Number of row in table = ten loai tai san + total tai san
        row_count = 1 + len(tai_san_list)
        self.setRowCount(row_count)
        self.setSpan(0, 0, 1, column_count)  # Merge cells
        setTableTextCell(table=self,
                         text=loai_tai_san.ten,
                         row=0,
                         col=0)
        row = 1
        stt = 1
        for tai_san in tai_san_list:
            items = [
                f"{stt}",
                f"{phong.don_vi.ma}.{phong.ma}.{loai_tai_san.ma}.{tai_san.ma}",
                tai_san.mo_ta if tai_san.mo_ta else '',
                tai_san.ghi_chu if tai_san.ghi_chu else ''
            ]
            for col, item in enumerate(items):
                setTableTextCell(table=self,
                                 text=item if item else '',
                                 row=row,
                                 col=col)

            row += 1
            stt += 1
        # Custom display for cols and rows of table
        self.resizeColumnsToContents()
        self.resizeRowsToContents()


class Widget_CreateQR(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # Create widgets
        self.label = QLabel('Enter text:')
        self.text_input = QLineEdit()
        self.generate_button = QPushButton('Generate QR Code')
        self.generate_button.clicked.connect(self.generate_qr_code)

        # Set up the layout
        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.text_input)
        layout.addWidget(self.generate_button)

        # Set up the main window
        self.setWindowTitle('QR Code Generator')
        self.setGeometry(100, 100, 400, 200)

    def generate_qr_code(self):
        data = self.text_input.text()

        if not data:
            return  # Do nothing if the input is empty

        # Open a file dialog to get the save path
        file_dialog = QFileDialog(self)
        file_dialog.setDefaultSuffix('png')
        file_path, _ = file_dialog.getSaveFileName(
            self, 'Save QR Code As', '', 'Images (*.png)')

        if file_path:
            self.save_qr_code(data, file_path)

    def save_qr_code(self, data, file_path):
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,
            border=2,
        )

        # Add data to the QR code
        qr.add_data(data)
        qr.make(fit=True)

        # Create an image from the QR code instance
        img = qr.make_image(fill_color="black", back_color="white")

        # Save the image to a file
        img.save(file_path)


class Widget_Database(QWidget):
    def __init__(self, parent: QWidget, models, callback_back=None, callback_select_table=None) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        frame_buttons = QFrame(self)
        frame_buttons_layout = QHBoxLayout(frame_buttons)
        # Set layout alignment to the left
        frame_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        pushButton_Back = QPushButton(parent=self, text="Quay lại")
        pushButton_Back.clicked.connect(callback_back)
        frame_buttons_layout.addWidget(pushButton_Back)
        self.layout.addWidget(frame_buttons)

        for model in models:
            pushButton_Model = QPushButton(
                parent=self, text=model.__tablename__)
            pushButton_Model.clicked.connect(
                partial(callback_select_table, model=model))
            self.layout.addWidget(pushButton_Model)
        spacer_widget = QWidget(parent=self)
        spacer_widget.setSizePolicy(QSizePolicy.Policy.Expanding,
                                    QSizePolicy.Policy.Expanding)
        self.layout.addWidget(spacer_widget)


class Widget_Database_Table(QWidget):
    def __init__(self,
                 parent: QWidget,
                 model,
                 callback_back=None,
                 callback_create=None,
                 callback_read=None,
                 callback_update=None,
                 callback_delete=None) -> None:
        super().__init__(parent)
        self.callback_back = callback_back
        self.callback_create = callback_create
        self.callback_read = callback_read
        self.callback_update = callback_update
        self.callback_delete = callback_delete
        self.layout = QVBoxLayout(self)
        self.model = model
        frame_buttons = QFrame(self)
        frame_buttons_layout = QHBoxLayout(frame_buttons)
        # Set layout alignment to the left
        frame_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        pushButton_Back = QPushButton(parent=self, text="Quay lại")
        pushButton_Back.clicked.connect(partial(self.back_button_clicked))
        frame_buttons_layout.addWidget(pushButton_Back)
        pushButton_Create = QPushButton(parent=self, text="Thêm mới")
        pushButton_Create.clicked.connect(partial(self.create_button_clicked))
        frame_buttons_layout.addWidget(pushButton_Create)
        self.layout.addWidget(frame_buttons)

        # Create a QTableWidget to display data
        table_widget = QTableWidget(self)

        # Set up the table headers based on model attributes
        column_count = len(model.__table__.columns) + \
            1  # +1 for the extra columna0=
        table_widget.setColumnCount(column_count)
        table_widget.setHorizontalHeaderLabels(
            [column.name for column in model.__table__.columns] + ["Chức năng"])

        # Populate the table with data
        populate_table(table_widget=table_widget,
                       model=model)

        # Add buttons to the last column for each row
        for row in range(table_widget.rowCount()):
            button_frame = QWidget(self)
            button_layout = QHBoxLayout(button_frame)
            read_button = QPushButton("", self)
            read_button.setIcon(QIcon(QPixmap(icon_show_path)))
            read_button.setStyleSheet(
                'background-color: rgba(0, 0, 255, 128);')
            read_button.clicked.connect(
                partial(self.read_button_clicked,
                        id=get_id_for_row(table_widget=table_widget,
                                          row=row)))
            button_layout.addWidget(read_button)
            update_button = QPushButton("", self)
            update_button.setIcon(QIcon(QPixmap(icon_edit_path)))
            update_button.setStyleSheet(
                'background-color: rgba(255, 255, 0, 128);')
            update_button.clicked.connect(
                partial(self.update_button_clicked,
                        id=get_id_for_row(table_widget=table_widget,
                                          row=row)))
            button_layout.addWidget(update_button)
            delete_button = QPushButton("", self)
            delete_button.setIcon(QIcon(QPixmap(icon_delete_path)))
            delete_button.setStyleSheet(
                'background-color: rgba(255, 0, 0, 127);')
            delete_button.clicked.connect(
                partial(self.delete_button_clicked,
                        id=get_id_for_row(table_widget=table_widget,
                                          row=row)))
            button_layout.addWidget(delete_button)
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_layout.setSpacing(0)

            table_widget.setCellWidget(row,
                                       column_count - 1,  # Last column
                                       button_frame)
        table_widget.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents)
        for col in range(1, column_count - 1):
            # Col from 1 to column - 2
            table_widget.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.Stretch)
        table_widget.horizontalHeader().setSectionResizeMode(
            column_count - 1, QHeaderView.ResizeMode.ResizeToContents)

        # Find the index of the column with the header "id"
        header_labels = [table_widget.horizontalHeaderItem(
            i).text() for i in range(table_widget.columnCount())]
        id_column_index = header_labels.index("id")

        # Hide the "id" column
        table_widget.setColumnHidden(id_column_index, True)

        table_widget.setSortingEnabled(True)
        table_widget.resizeColumnsToContents()
        table_widget.resizeRowsToContents()
        self.layout.addWidget(table_widget)

    def read_button_clicked(self, id):
        if not self.callback_read:
            return
        status, obj = get_crud_class(self.model).read(id)
        if status != CRUD_Status.FOUND:
            return
        self.callback_read(obj=obj)

    def update_button_clicked(self, id):
        if not self.callback_update:
            return
        status, obj = get_crud_class(self.model).read(id)
        if status != CRUD_Status.FOUND:
            return
        self.callback_update(obj=obj)

    def delete_button_clicked(self, id):
        if not self.callback_delete:
            return
        status, obj = get_crud_class(self.model).read(id)
        print(status, obj)
        if status != CRUD_Status.FOUND:
            return
        self.callback_delete(obj=obj)

    def back_button_clicked(self):
        if not self.callback_back:
            return
        self.callback_back()

    def create_button_clicked(self):
        if not self.callback_create:
            return
        self.callback_create(model=self.model)

# Assuming you have a function to populate the table, you can replace this with your actual implementation


def get_id_for_row(table_widget, row):
    header_labels = [table_widget.horizontalHeaderItem(col).text()
                     for col in range(table_widget.columnCount())]

    id_column_index = header_labels.index(
        "id") if "id" in header_labels else -1

    if id_column_index != -1:
        id_item = table_widget.item(row, id_column_index)
        if id_item:
            return int(id_item.text())
    return None


def populate_table(table_widget, model):
    # Retrieve all instances of the model from the database
    instances = session.query(model).all()

    # Set the number of rows in the table
    table_widget.setRowCount(len(instances))

    # Populate the table with data
    for row, instance in enumerate(instances):
        for col, column in enumerate(model.__table__.columns):
            if column.foreign_keys:
                # If the column is a foreign key, get the related instance
                foreign_key_instance_id = getattr(instance, column.name)
                related_model = list(column.foreign_keys)[0].column.table
                related_instance = session.query(related_model).filter_by(
                    id=foreign_key_instance_id).first()
                item_text = str(related_instance)
            else:
                item_text = str(getattr(instance, column.name))

            item = QTableWidgetItem(item_text)
            table_widget.setItem(row, col, item)


class Widget_ReadUpdateDelete(QWidget):
    """
    Read: callback_update = None\n
    or\n
    Update: callback_update = callback_update\n
    Disable Delete: callback_delete = None\n
    or\n
    Enable Delete: callback_delete = callback_delete\n
    """

    def __init__(self,
                 parent: QWidget,
                 obj: Base,
                 callback_back=None,
                 callback_cancel=None,
                 callback_update=None,
                 callback_delete=None) -> None:
        super().__init__(parent)
        self.callback_back = callback_back
        self.callback_cancel = callback_cancel
        self.callback_update = callback_update
        self.callback_delete = callback_delete
        self.layout = QVBoxLayout(self)
        self.obj = obj
        self.model = type(obj)
        self.line_edits = {}
        self.comboboxes = {}
        frame_buttons = QFrame(self)
        frame_buttons_layout = QHBoxLayout(frame_buttons)
        # Set layout alignment to the left
        frame_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        pushButton_Back = QPushButton(parent=self, text="Quay lại")
        pushButton_Back.clicked.connect(partial(self.back_button_clicked))
        frame_buttons_layout.addWidget(pushButton_Back)
        self.layout.addWidget(frame_buttons)
        # Get the mapped class and its properties using inspect
        mapper = inspect(self.model)

        for column in mapper.columns:
            # Skip the 'id' column or any other columns you want to exclude
            if column.name == 'id':
                continue
            label_name = QLabel(column.name, parent=self)
            self.layout.addWidget(label_name)
            # Check if the column is a foreign key
            if column.foreign_keys:

                combobox = QComboBox(self)
                # Add a "None" option as the first item
                combobox.addItem("None", None)
                # Add all instances
                related_model = session.query(
                    list(column.foreign_keys)[0].column.table).all()

                for instance in related_model:
                    combobox.addItem(
                        str(instance), getattr(instance, 'id', None))

                current_value = getattr(self.obj, column.name, None)
                index = combobox.findData(current_value)
                combobox.setCurrentIndex(index)

                self.comboboxes[column.name] = combobox
                self.layout.addWidget(combobox)
            else:
                line_edit_input = QLineEdit(
                    str(getattr(self.obj, column.name, '')), parent=self)
                # Enable clear button for QLineEdit
                line_edit_input.setClearButtonEnabled(True)
                self.line_edits[column.name] = line_edit_input
                self.layout.addWidget(line_edit_input)

        print(self.line_edits)
        print(self.comboboxes)
        spacer_widget = QWidget(parent=self)
        spacer_widget.setSizePolicy(QSizePolicy.Policy.Expanding,
                                    QSizePolicy.Policy.Expanding)
        self.layout.addWidget(spacer_widget)

        # Frame for action buttons
        frame_buttons = QFrame(self)
        frame_buttons_layout = QVBoxLayout(frame_buttons)

        # Update mode
        if callback_update:
            update_button = QPushButton("Cập nhật", self)
            update_button.clicked.connect(partial(self.update_button_clicked))
            frame_buttons_layout.addWidget(update_button)
        # Read mode
        else:
            self.set_read_mode()
        if callback_delete:
            delete_button = QPushButton("Xoá", self)
            delete_button.clicked.connect(partial(self.delete_button_clicked))
            frame_buttons_layout.addWidget(delete_button)
        if callback_update or callback_delete:
            cancel_button = QPushButton("Huỷ", self)
            cancel_button.clicked.connect(partial(self.cancel_button_clicked))
            frame_buttons_layout.addWidget(cancel_button)
        self.layout.addWidget(frame_buttons)
        self.setLayout(self.layout)

    def back_button_clicked(self):
        if not self.callback_back:
            return
        self.callback_back(model=self.model)

    def set_read_mode(self):
        for line_edit in self.line_edits.values():
            line_edit.setReadOnly(True)

        for combobox in self.comboboxes.values():
            combobox.show()
            combobox.setEditable(True)
            combobox.lineEdit().setReadOnly(True)

    def cancel_button_clicked(self):
        if self.callback_cancel:
            self.callback_cancel(model=self.model)

    def update_button_clicked(self):
        if not self.callback_update:
            return
        # Update the model object with user input
        for name, line_edit in self.line_edits.items():
            setattr(self.obj,
                    name,
                    line_edit.text() if line_edit.text() != '' else None)

        # Set foreign key values
        for column_name, combobox in self.comboboxes.items():
            selected_instance_id = combobox.currentData()
            setattr(self.obj, column_name, selected_instance_id)

        model_values = {name: getattr(self.obj, name, None)
                        for name in self.line_edits.keys()}
        self.callback_update(obj=self.obj,
                             **model_values)

    def delete_button_clicked(self):
        if not self.callback_delete:
            return
        self.callback_delete(obj=self.obj)


class Widget_Create(QWidget):
    def __init__(self, parent: QWidget, model: Base, callback_back=None, callback_cancel=None, callback_create=None) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.model = model

        self.line_edits = {}
        self.comboboxes = {}

        frame_buttons = QFrame(self)
        frame_buttons_layout = QHBoxLayout(frame_buttons)
        # Set layout alignment to the left
        frame_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        pushButton_Back = QPushButton(parent=self, text="Quay lại")
        pushButton_Back.clicked.connect(partial(self.back_button_clicked,
                                                callback_back=callback_back))
        frame_buttons_layout.addWidget(pushButton_Back)
        pushButton_Create = QPushButton(parent=self, text="Thêm mới")
        pushButton_Create.clicked.connect(partial(self.create_button_clicked,
                                                  callback_create=callback_create,
                                                  model=model))
        frame_buttons_layout.addWidget(pushButton_Create)
        self.layout.addWidget(frame_buttons)

        mapper = class_mapper(self.model)

        for prop in mapper.iterate_properties:
            if hasattr(prop, 'columns') and len(prop.columns) == 1:
                column = prop.columns[0]
                # Skip the 'id' column or any other columns you want to exclude
                if column.name == 'id':
                    continue
                label_name = QLabel(column.name, parent=self)
                self.layout.addWidget(label_name)
                # Check if the column is a foreign key
                if column.foreign_keys:
                    combobox = QComboBox(self)
                    # Add a "None" option as the first item
                    combobox.addItem("None", None)
                    # Add all instances
                    related_model = column.foreign_keys.pop().column.table
                    related_instances = session.query(related_model).all()

                    for instance in related_instances:
                        combobox.addItem(str(instance), instance.id)

                    self.comboboxes[column.name] = combobox
                    self.layout.addWidget(combobox)
                else:
                    line_edit_input = QLineEdit(parent=self)
                    # Enable clear button for QLineEdit
                    line_edit_input.setClearButtonEnabled(True)
                    self.line_edits[column.name] = line_edit_input
                    self.layout.addWidget(line_edit_input)
        spacer_widget = QWidget(parent=self)
        spacer_widget.setSizePolicy(QSizePolicy.Policy.Expanding,
                                    QSizePolicy.Policy.Expanding)
        self.layout.addWidget(spacer_widget)
        cancel_button = QPushButton("Huỷ", self)
        cancel_button.clicked.connect(partial(self.cancel_button_clicked,
                                              callback_cancel=callback_cancel))

        create_button = QPushButton("Tạo", self)
        create_button.clicked.connect(partial(self.create_button_clicked,
                                              callback_create=callback_create))

        frame_buttons = QFrame(self)
        frame_buttons_layout = QHBoxLayout(frame_buttons)
        frame_buttons_layout.addWidget(cancel_button)
        frame_buttons_layout.addWidget(create_button)
        self.layout.addWidget(frame_buttons)
        self.setLayout(self.layout)

        # self.setLayout(self.layout)

    def back_button_clicked(self, callback_back):
        callback_back(model=self.model)

    def cancel_button_clicked(self, callback_cancel):
        callback_cancel(model=self.model)

    def create_button_clicked(self, callback_create):
        # Create the model object with user input
        model_values = {name: line_edit.text() if line_edit.text() != '' else None
                        for name, line_edit in self.line_edits.items()}

        # Set foreign key values
        for column_name, combobox in self.comboboxes.items():
            selected_instance_id = combobox.currentData()
            model_values[column_name] = selected_instance_id

        callback_create(model=self.model, **model_values)
