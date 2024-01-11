from collections import defaultdict
import signal
import typing
# PyQt6
from functools import partial
import PyQt6
from PyQt6 import QtWidgets

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import (
    QPixmap,
    QIcon,
    QColor
)
import qrcode

from Backend.Database.db_sessions import *


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
        file_path, _ = file_dialog.getSaveFileName(self, 'Save QR Code As', '', 'Images (*.png)')

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
