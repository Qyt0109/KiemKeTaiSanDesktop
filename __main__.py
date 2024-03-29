from Backend.Database.db_sessions import *
from Frontend.Helper.helper import *
from Frontend.Design.design_ui import Ui_MainWindow
from collections import defaultdict
import signal
import typing
# PyQt6
from functools import partial
import PyQt6
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QWidget,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QTableWidgetItem,
    QHeaderView
)
from PyQt6.QtCore import Qt, QTimer, QCoreApplication
from PyQt6.QtGui import (
    QPixmap,
    QIcon,
    QColor
)

""" Modules """
""" Frontend """
# The design
# Dynamic render view and other helper for UI
""" Backend """
# Database

TEST_DEV = False


def resetAllTaiSan():
    status, tai_sans = CRUD_TaiSan.read_all()
    for tai_san in tai_sans:
        CRUD_TaiSan.update(id=tai_san.id,
                           ghi_chu=BanGhiKiemKeState.NOT_AVAILABLE.value)

# if TEST_DEV:
    # resetAllTaiSan()



class PageRoomsInfoMode(Enum):
    DANH_SACH = "Danh sách"
    KIEM_KE = "Kiểm kê"


class MyApplication(QMainWindow):
    """ Main App class """

    def __init__(self):
        super().__init__()
        # Set up the user interface from Designer
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.init_icons()

        # Extended design and setup for ui
        self.toPageLogin()  # Started at login page

        # Connect signals and slots
        self.ui.pushButton_Login.clicked.connect(self.login)

        """ Page Rooms """
        self.ui.pushButton_Rooms.clicked.connect(self.toPageRooms)
        self.ui.pushButton_RoomSearch.clicked.connect(
            self.onClicked_pushButton_RoomSearch)
        self.ui.pushButton_RoomSearch_ClearFilter.clicked.connect(
            self.onClicked_pushButton_RoomSearch_ClearFilter)
        self.ui.pushButton_RoomSearchOptions.clicked.connect(
            self.onClicked_pushButton_RoomSearchOptions)
        self.ui.pushButton_Home.clicked.connect(self.toPageMainMenu)
        self.ui.pushButton_Back.clicked.connect(self.toPageMainMenu)
        self.ui.pushButton_RoomSearchOptions.setStyleSheet(
            "background-color: rgba(255, 255, 255, 128);")
        self.ui.frame_RoomSearchOptions.setVisible(False)
        """ Page Rooms """
        """ Page Room Info """
        self.ui.pushButton_RoomInfo_Home.clicked.connect(self.toPageMainMenu)
        self.ui.pushButton_RoomInfo_Back.clicked.connect(
            self.toPageRooms)
        """ Page Room Info """
        """ Page Database """
        self.ui.pushButton_Database.clicked.connect(self.toPageDatabase)
        """ Page Database """
        """ Page CreateQR """
        self.ui.frame_CreateQR.layout().addWidget(
            Widget_CreateQR(parent=self.ui.frame_CreateQR))
        self.ui.pushButton_ToPageCreateQR.clicked.connect(self.toPageCreateQR)
        self.ui.pushButton_CreateQR_Home.clicked.connect(self.toPageMainMenu)
        self.ui.pushButton_CreateQR_Back.clicked.connect(
            self.toPageMainMenu)
        """ Page CreateQR """

        # Full screen
        # self.showFullScreen()
        if TEST_DEV:
            self.toPageMainMenu()

    # Icons
    def init_icons(self):
        """ Page Rooms """
        self.ui.pushButton_RoomSearch.setIcon(QIcon(QPixmap(icon_search_path)))
        self.ui.pushButton_RoomSearch_ClearFilter.setIcon(
            QIcon(QPixmap(icon_x_path)))
        self.ui.pushButton_RoomSearchOptions.setIcon(
            QIcon(QPixmap(icon_options_path)))
        self.ui.pushButton_Home.setIcon(QIcon(QPixmap(icon_home_path)))
        self.ui.pushButton_Back.setIcon(QIcon(QPixmap(icon_back_path)))
        """ Page Rooms """
        """ Page RoomInfo """
        self.ui.pushButton_RoomInfo_Home.setIcon(
            QIcon(QPixmap(icon_home_path)))
        self.ui.pushButton_RoomInfo_Back.setIcon(
            QIcon(QPixmap(icon_back_path)))
        self.ui.pushButton_RoomInfo_Refresh.setIcon(
            QIcon(QPixmap(icon_refresh_path)))
        """ Page RoomInfo """
        """ Page CreateQR """
        self.ui.pushButton_CreateQR_Home.setIcon(
            QIcon(QPixmap(icon_home_path)))
        self.ui.pushButton_CreateQR_Back.setIcon(
            QIcon(QPixmap(icon_back_path)))
        """ Page CreateQR """

    # Define functions
    def login(self):
        if self.ui.lineEdit_Username.text() == "admin" and self.ui.lineEdit_Password.text() == "admin":
            print("Logged in!")
            self.toPageMainMenu()
        # Bypass login for developing
        else:
            self.toPageMainMenu()

    def toPageLogin(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_Login)

    def toPageMainMenu(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_MainMenu)

    def renderRooms(self):
        qpushbutton_clicked_disconnect(self.ui.pushButton_RoomInfo_Back)
        self.ui.pushButton_RoomInfo_Back.clicked.connect(
            self.toPageRooms)
        status, result = CRUD_DonVi.read_all()
        don_vis = []
        if status == CRUD_Status.FOUND:
            don_vis = result
        else:
            print(status, result)
        self.ui.comboBox_RoomSearchOptions_DonVi.clear()
        self.ui.comboBox_RoomSearchOptions_DonVi.addItem("")  # INDEX 0 OPTION
        for don_vi in don_vis:
            self.ui.comboBox_RoomSearchOptions_DonVi.addItem(don_vi.ten)
        parent = self.ui.frame_KhuHolder
        layout = parent.layout()
        clearAllWidgets(parent)
        status, result = CRUD_Khu.read_all()
        khus = []
        if status == CRUD_Status.FOUND:
            khus = result
        else:
            print(status, result)
        for khu in khus:
            frame_Khu = Frame_Khu(parent=parent,
                                  khu=khu,
                                  callback_pushButton_Phong=self.toPageRoomInfo)
            layout.addWidget(frame_Khu)
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_Rooms)

    """ Page Rooms """

    def toPageRooms(self):
        self.renderRooms()

    def onClicked_pushButton_RoomSearch_ClearFilter(self):
        self.ui.lineEdit_RoomSearch.setText(None)
        self.ui.comboBox_RoomSearchOptions_DonVi.setCurrentIndex(0)

    def onClicked_pushButton_RoomSearch(self):
        selected_don_vi_id = None
        if self.ui.comboBox_RoomSearchOptions_DonVi.isVisible():
            selected_don_vi_index = self.ui.comboBox_RoomSearchOptions_DonVi.currentIndex()
            # NOT INDEX 0 OPTION
            if selected_don_vi_index != 0:
                selected_don_vi = self.don_vis[selected_don_vi_index - 1]
                selected_don_vi_id = selected_don_vi.id
        """ Filtered search
        phongs = search_phong_by_filter(substring=self.ui.lineEdit_RoomSearch.text(),
                                        don_vi_id=selected_don_vi_id)
        for phong in phongs:
            print(phong.ten)
        """

    def toPageDatabase(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_List)
        parent = self.ui.scrollAreaWidgetContents_List
        parent_layout = parent.layout()
        clearAllWidgets(parent)
        models = all_models
        widget_database = Widget_Database(parent=parent,
                                          models=models,
                                          callback_back=self.toPageMainMenu,
                                          callback_select_table=self.toPageDatabase_Table)
        parent_layout.addWidget(widget_database)

    def toPageDatabase_Table(self, model):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_List)
        parent = self.ui.scrollAreaWidgetContents_List
        parent_layout = parent.layout()
        clearAllWidgets(parent)
        widget_table = Widget_Database_Table(parent=parent,
                                    model=model,
                                    callback_back=self.toPageDatabase,
                                    callback_create=self.toPageDatabase_Table_CreateData,
                                    callback_read=self.toPageDatabase_Table_Read,
                                    callback_update=self.toPageDatabase_Table_Update,
                                    callback_delete=self.toPageDatabase_Table_Delete)
        parent_layout.addWidget(widget_table)
    
    def toPageDatabase_Table_Delete(self, obj):
        self.deleteData(obj)

    def toPageDatabase_Table_Update(self, obj):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_List)
        parent = self.ui.scrollAreaWidgetContents_List
        parent_layout = parent.layout()
        clearAllWidgets(parent)
        widget_update = Widget_ReadUpdateDelete(parent=parent,
                                      obj=obj,
                                      callback_back=self.toPageDatabase_Table,
                                      callback_cancel=self.toPageDatabase_Table,
                                      callback_update=self.updateData,
                                      callback_delete=self.deleteData)
        
        parent_layout.addWidget(widget_update)

    def deleteData(self, obj):
        model = type(obj)
        CRUD_Model = get_crud_class(model_class=model)
        status, result = CRUD_Model.delete(id=obj.id)
        print(status, result)
        if status != CRUD_Status.DELETED:
            return
        self.toPageDatabase_Table(model=model)
    
    def updateData(self, obj, **kwargs):
        model = type(obj)
        CRUD_Model = get_crud_class(model_class=model)
        status, result = CRUD_Model.update(id=obj.id,
                                           **kwargs)
        print(status, result)
        if status != CRUD_Status.UPDATED:
            return
        self.toPageDatabase_Table(model=model)
    
    def toPageDatabase_Table_Read(self, obj):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_List)
        parent = self.ui.scrollAreaWidgetContents_List
        parent_layout = parent.layout()
        clearAllWidgets(parent)
        widget_create = Widget_ReadUpdateDelete(parent=parent,
                                      obj=obj,
                                      callback_back=self.toPageDatabase_Table,
                                      callback_cancel=self.toPageDatabase_Table,
                                      callback_update=None,
                                      callback_delete=None)
        
        parent_layout.addWidget(widget_create)

    def toPageDatabase_Table_CreateData(self, model):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_List)
        parent = self.ui.scrollAreaWidgetContents_List
        parent_layout = parent.layout()
        clearAllWidgets(parent)
        widget_create = Widget_Create(parent=parent,
                                      model=model,
                                      callback_back=self.toPageDatabase_Table,
                                      callback_cancel=self.toPageDatabase_Table,
                                      callback_create=self.createData)
        
        parent_layout.addWidget(widget_create)
        
    def createData(self, model, **kwargs):
        CRUD_Model = get_crud_class(model_class=model)
        status, result = CRUD_Model.create(**kwargs)
        print(status, result)
        if status != CRUD_Status.CREATED:
            return
        self.toPageDatabase_Table(model=model)

    def toPageDatabase_Table_Data(self, data):
        pass

    def onClicked_pushButton_RoomSearchOptions(self):
        is_visible = self.ui.frame_RoomSearchOptions.isVisible()
        self.ui.frame_RoomSearchOptions.setVisible(not is_visible)

        # Set color based on visibility
        if is_visible:
            self.ui.pushButton_RoomSearchOptions.setStyleSheet(
                "background-color: rgba(255, 255, 255, 128);")
        else:
            self.ui.pushButton_RoomSearchOptions.setStyleSheet(
                "background-color: rgba(102, 153, 255, 128);")
    """ Page Rooms """

    """ Page CreateQR """

    def toPageCreateQR(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_CreateQR)
    """ Page CreateQR """

    """ Page Room info """

    def toPageRoomInfo(self, phong):
        qpushbutton_clicked_disconnect(self.ui.pushButton_RoomInfo_Refresh)
        self.ui.pushButton_RoomInfo_Refresh.clicked.connect(
            lambda: self.renderViewRoomInfo_DanhMuc(phong=phong)
        )
        parent = self.ui.frame_RoomInfo
        clearAllWidgets(parent_widget=parent)
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_RoomInfo)
        self.renderViewRoomInfo_Info(phong)
        qpushbutton_clicked_disconnect(self.ui.pushButton_RoomInfo_Info)
        self.ui.pushButton_RoomInfo_Info.clicked.connect(
            lambda: self.renderViewRoomInfo_Info(phong=phong))

        self.ui.pushButton_RoomInfo_DanhMuc.setHidden(False)
        qpushbutton_clicked_disconnect(
            self.ui.pushButton_RoomInfo_DanhMuc)
        self.ui.pushButton_RoomInfo_DanhMuc.clicked.connect(
            lambda: self.renderViewRoomInfo_DanhMuc(phong=phong))

    def renderViewRoomInfo_Info(self, phong):
        qpushbutton_clicked_disconnect(self.ui.pushButton_RoomInfo_Back)
        self.ui.pushButton_RoomInfo_Back.clicked.connect(
            self.toPageRooms)
        self.ui.label_RoomInfo_TenPhong.setText(
            f"Phòng {phong.ma} - {phong.khu.ten}\n{phong.ten}")
        # Setup frame for display RoomInfo_Info
        parent = self.ui.frame_RoomInfo
        parent_layout = parent.layout()
        clearAllWidgets(parent_widget=parent)
        # Frame for RoomInfo_Info to be setted in frame_RoomInfo
        frame_RoomInfo_Info = Frame_RoomInfo_Info(parent=parent,
                                                  phong=phong)
        parent_layout.addWidget(frame_RoomInfo_Info)

    def renderViewRoomInfo_DanhMuc(self, phong):
        qpushbutton_clicked_disconnect(self.ui.pushButton_RoomInfo_Back)
        self.ui.pushButton_RoomInfo_Back.clicked.connect(
            self.toPageRooms)
        """ Tạo view danh mục """
        self.ui.label_RoomInfo_TenPhong.setText(
            f"Phòng {phong.ma} - {phong.khu.ten}\n{phong.ten}")
        # Setup frame for display RoomInfo_Info
        parent = self.ui.frame_RoomInfo
        parent_layout = parent.layout()
        clearAllWidgets(parent_widget=parent)
        table_DanhMuc = Table_DanhMuc(parent=parent,
                                      phong=phong,
                                      callback_DetailButton=self.renderViewRoomInfo_DanhMuc_Detail)
        parent_layout.addWidget(table_DanhMuc)

    def renderViewRoomInfo_DanhMuc_Detail(self, phong: Phong, loai_tai_san: LoaiTaiSan, tai_san_list: List[TaiSan]):
        qpushbutton_clicked_disconnect(self.ui.pushButton_RoomInfo_Refresh)
        self.ui.pushButton_RoomInfo_Refresh.clicked.connect(
            lambda: self.renderViewRoomInfo_DanhMuc_Detail(
                phong=phong, loai_tai_san=loai_tai_san, tai_san_list=tai_san_list)
        )
        qpushbutton_clicked_disconnect(self.ui.pushButton_RoomInfo_Back)
        self.ui.pushButton_RoomInfo_Back.clicked.connect(
            partial(self.renderViewRoomInfo_DanhMuc, phong=phong))
        self.ui.label_RoomInfo_TenPhong.setText(
            f"Phòng {phong.ma} - {phong.khu.ten}\n{phong.ten}")
        # Setup frame for display RoomInfo_Info
        parent = self.ui.frame_RoomInfo
        parent_layout = parent.layout()
        clearAllWidgets(parent_widget=parent)

        table_DanhMuc_Detail = Table_DanhMuc_Detail(parent=parent,
                                                    phong=phong,
                                                    loai_tai_san=loai_tai_san,
                                                    tai_san_list=tai_san_list)
        parent_layout.addWidget(table_DanhMuc_Detail)

    """ Page Room info """


def qpushbutton_clicked_disconnect(button: QPushButton):
    try:
        button.clicked.disconnect()
    except Exception:
        pass


if __name__ == "__main__":
    app = QApplication([])
    window = MyApplication()
    window.show()
    app.exec()
