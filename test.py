from Backend.Database.db_sessions import *
from Frontend.Helper.helper import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget        

if __name__ == "__main__":
    app = QApplication([])
    #"""
    status, result = CRUD_TaiSan.read(13)
    window = Widget_ReadUpdateDelete(parent=None, obj=result, callback_update=CRUD_TaiSan.update, callback_delete=CRUD_TaiSan.delete)
    # """
    """
    window = Widget_Create(parent=None, model=TaiSan, callback_create=None)
    # """
    window.show()
    app.exec()