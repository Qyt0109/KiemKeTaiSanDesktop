from sqlalchemy.orm import make_transient
from enum import Enum, EnumMeta
from typing import Callable, List, Tuple
from Backend.Database.db_models import *
from Backend.Database.connection_string import connection_password
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

db_type = 'mysql'
db_connector_module = 'pymysql'
db_host = 'gateway01.ap-northeast-1.prod.aws.tidbcloud.com'
db_port = '4000'
db_username = '3xKs6MSRB2UKUd5.root'
db_ssl_ca_path = '/etc/ssl/cert.pem'
db_password = connection_password

# Create an SQLite engine
ECHO = False
TEST_DB = False
if TEST_DB:
    connection_string_url = 'sqlite:///Backend/Database/db.sqlite'
else:
    connection_string_url = f"{db_type}+{db_connector_module}://{db_username}:{db_password}@{db_host}:{db_port}/test?ssl_ca={db_ssl_ca_path}&ssl_verify_cert=true&ssl_verify_identity=true"
engine = create_engine(connection_string_url, echo=ECHO)

# Create the table in the database
try:
    Base.metadata.create_all(engine)
except Exception as e:
    print(e)

# Create a session factory
Session = sessionmaker(bind=engine)
# default_session = Session()

session = Session()


class CRUD_Status(Enum):
    CREATED = 'Đã tạo'
    FOUND = 'Tìm thấy'
    NOT_FOUND = 'Không tìm thấy'
    UPDATED = 'Đã cập nhật'
    DELETED = 'Đã xoá'
    ERROR = 'Lỗi'


def crud_handler_wrapper(func: Callable) -> Tuple[CRUD_Status, any]:
    def wrapper(*args, **kwargs) -> Tuple[CRUD_Status, any]:
        try:
            result = func(*args, **kwargs)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            return CRUD_Status.ERROR, e
    return wrapper


def read_handler_wrapper(func: Callable) -> Tuple[CRUD_Status, any]:
    def wrapper(*args, **kwargs) -> Tuple[CRUD_Status, any]:
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            return CRUD_Status.ERROR, e
    return wrapper


class CRUD_Base:
    # Subclasses should define the SQLAlchemy model class
    model = None

    @classmethod
    @crud_handler_wrapper
    def create(cls, **kwargs) -> Tuple[CRUD_Status, any]:
        new_instance = cls.model(**kwargs)
        print(new_instance)
        session.add(new_instance)
        return CRUD_Status.CREATED, new_instance

    @classmethod
    @read_handler_wrapper
    def read(cls, id: int) -> Tuple[CRUD_Status, any]:
        found_instance = session.query(cls.model).get(id)
        if not found_instance:
            return CRUD_Status.NOT_FOUND, None
        return CRUD_Status.FOUND, found_instance

    @classmethod
    @read_handler_wrapper
    def read_all(cls) -> Tuple[CRUD_Status, List[any]]:
        found_instances = session.query(cls.model).all()
        if not found_instances:
            return CRUD_Status.NOT_FOUND, []
        return CRUD_Status.FOUND, found_instances

    @classmethod
    @crud_handler_wrapper
    def update(cls, id: int, **kwargs) -> Tuple[CRUD_Status, any]:
        state, found_instance = cls.read(id)
        if state == CRUD_Status.NOT_FOUND:
            return CRUD_Status.NOT_FOUND, None
        for key, value in kwargs.items():
            setattr(found_instance, key, value)
        return CRUD_Status.UPDATED, found_instance

    @classmethod
    @crud_handler_wrapper
    def delete(cls, id: int) -> Tuple[CRUD_Status, any]:
        state, found_instance = cls.read(id)
        if state == CRUD_Status.NOT_FOUND:
            return CRUD_Status.NOT_FOUND, None
        session.delete(found_instance)
        return CRUD_Status.DELETED, None


class CRUD_Khu(CRUD_Base):
    model = Khu


class CRUD_CanBo(CRUD_Base):
    model = CanBo


class CRUD_DonVi(CRUD_Base):
    model = DonVi


class CRUD_Phong(CRUD_Base):
    model = Phong


class CRUD_NhomTaiSan(CRUD_Base):
    model = NhomTaiSan


class CRUD_LoaiTaiSan(CRUD_Base):
    model = LoaiTaiSan


class CRUD_TaiSan(CRUD_Base):
    model = TaiSan


class CRUD_LichSuKiemKe(CRUD_Base):
    model = LichSuKiemKe


class CRUD_BanGhiKiemKe(CRUD_Base):
    model = BanGhiKiemKe

def get_crud_class(model_class)->CRUD_Base:
    # Assuming that the CRUD classes are defined in the same module
    crud_class_name = f"CRUD_{model_class.__name__}"

    # Use globals() to get the class from the global namespace
    crud_class = globals().get(crud_class_name)

    return crud_class


class BanGhiKiemKeState(Enum):
    NOT_AVAILABLE = "Chưa kiểm"
    IS_AVAILABLE = "Đã kiểm"
    NEW_INCLUDE = "Đã nhập"


class Handler_KiemKe:
    def __init__(self, phong_id: int) -> None:
        self.lich_su_kiem_ke = None
        self.ban_ghi_kiem_ke = None
        self.init_me(phong_id=phong_id)

    def init_me(self, phong_id: int):
        try:
            lich_su_kiem_ke = LichSuKiemKe(phong_id=phong_id)
            session.add(lich_su_kiem_ke)
            session.commit()  # Commit to get the ID
            self.lich_su_kiem_ke = lich_su_kiem_ke

            ban_ghi_kiem_ke = BanGhiKiemKe(
                thoi_gian=datetime.now(), lich_su_kiem_ke_id=lich_su_kiem_ke.id)
            session.add(ban_ghi_kiem_ke)
            session.commit()  # Commit to get the ID
            self.ban_ghi_kiem_ke = ban_ghi_kiem_ke

        except Exception as e:
            print(f"Error: {e}")

    def add_tai_san(self, tai_san_id: int, trang_thai: str = BanGhiKiemKeState.NOT_AVAILABLE):
        tai_san = CRUD_TaiSan.read(tai_san_id=tai_san_id)
        if not tai_san:
            return CRUD_Status.NOT_FOUND

        association = ban_ghi_kiem_ke_tai_san_association.insert().values(
            tai_san_id=tai_san_id,
            ban_ghi_kiem_ke_id=self.ban_ghi_kiem_ke.id,
            trang_thai=trang_thai
        )
        session.execute(association)

    def complete(self):
        try:
            self.lich_su_kiem_ke.thoi_gian = datetime.now()
            # Add the transient objects to the session and commit
            session.commit()
        except Exception as e:
            print(f"Error completing kiem ke: {e}")
            session.rollback()
