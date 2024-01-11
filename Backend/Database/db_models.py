from datetime import datetime
from sqlalchemy import Table, create_engine, ForeignKey, Column, Integer, Float, BLOB,Boolean, DATETIME, String, LargeBinary, DateTime, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Create a base class for declarative models
Base = declarative_base()

"""
1 Khu có nhiều Phòng, Phòng chỉ thuộc về 1 Khu
Khu 1-n Phong
1 Đơn Vị có nhiều Phòng, Phòng chỉ thuộc về 1 Đơn vị
DonVi 1-n Phong
1 Cán Bộ có nhiều Phòng, Phòng chỉ thuộc về 1 Cán Bộ
CanBo 1-n Phong
1 Nhóm Tài Sản có nhiều Loại Tài Sản, Loại Tài Sản chỉ thuộc về 1 Nhóm Tài Sản
NhomTaiSan 1-n LoaiTaiSan
1 Loại Tài Sản có nhiều Tài Sản, Tài Sản chỉ thuộc về 1 Loại Tài Sản
LoaiTaiSan 1-n TaiSan
1 Phòng có nhiều Tài Sản, Tài Sản chỉ thuộc về 1 Phòng
Phong 1-n TaiSan
"""

class Khu(Base):
    __tablename__ = 'khu'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten = Column(String(length=255), nullable=False, unique=True)   # Khu không được trùng tên

    # 1-n Relationships
    phongs = relationship("Phong", back_populates="khu")

class CanBo(Base):
    __tablename__ = "can_bo"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten = Column(String(length=255), nullable=False)    # Cán bộ có thể trùng tên
    sdt = Column(String(length=255))
    # 1-n Relationships
    phongs = relationship("Phong", back_populates="can_bo")

class DonVi(Base):
    __tablename__ = "don_vi"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten = Column(String(length=255), nullable=False, unique=False)   # Đơn vị có thể trùng tên
    ma = Column(String(length=255), nullable=False, unique=True)   # Đơn vị không được trùng mã
    # 1-n Relationships
    phongs = relationship("Phong", back_populates="don_vi")

class Phong(Base):
    __tablename__ = 'phong'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten = Column(String(length=255), nullable=False, unique=False)   # Phòng có thể trùng tên (VD Phòng thực tập)
    ma = Column(String(length=255), nullable=False, unique=False)   # Phòng có thể trùng mã (VD P201) nhưng thuộc các khu, đơn vị,... khác nhau nên không thành vấn đề
    thong_tin = Column(String(length=255))
    # n-1 Relationships
    khu_id = Column(Integer, ForeignKey('khu.id'))
    khu = relationship("Khu", back_populates="phongs")
    don_vi_id = Column(Integer, ForeignKey('don_vi.id'))
    don_vi = relationship("DonVi", back_populates="phongs")
    can_bo_id = Column(Integer, ForeignKey('can_bo.id'))
    can_bo = relationship("CanBo",  back_populates="phongs")
    # 1-n Relationships
    tai_sans = relationship("TaiSan", back_populates="phong")
    lich_su_kiem_kes = relationship("LichSuKiemKe", back_populates="phong")
    

class NhomTaiSan(Base):
    __tablename__ = "nhom_tai_san"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten = Column(String(length=255), nullable=False, unique=True)   # Không có nhóm tài sản nào trùng tên nhau (VD không thể Máy tính, Máy tính)
    # 1-n Relationships
    loai_tai_sans = relationship("LoaiTaiSan", back_populates="nhom_tai_san")

class LoaiTaiSan(Base):
    __tablename__ = "loai_tai_san"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten = Column(String(length=255), nullable=False, unique=False)  # Loại tài sản có thể trùng tên, nhưng thuộc về các nhóm tài sản khác nhau
    ma = Column(String(length=255), nullable=False, unique=False)   # Loại tài sản có thể trùng mã, nhưng thuộc về các nhóm tài sản khác nhau
    # n-1 Relationships
    nhom_tai_san_id = Column(Integer, ForeignKey('nhom_tai_san.id'))
    nhom_tai_san = relationship('NhomTaiSan', back_populates='loai_tai_sans')
    # 1-n Relationships
    tai_sans = relationship("TaiSan", back_populates="loai_tai_san")

class LichSuKiemKe(Base):
    """ Lịch Sử Kiểm Kê là bảng lưu các lần kiểm kê của một phòng"""
    __tablename__ = "lich_su_kiem_ke"
    id = Column(Integer, primary_key=True, autoincrement=True)
    thoi_gian = Column(DateTime, default=datetime.utcnow())
    """ Thời gian gửi lên hệ thống """
    # n-1 relationships
    phong_id = Column(Integer, ForeignKey('phong.id'))
    """ ID của phòng được kiểm kê """
    phong = relationship('Phong', back_populates='lich_su_kiem_kes')
    """ Phòng được kiểm kê """
    # 1-n relationships
    ban_ghi_kiem_kes = relationship("BanGhiKiemKe", back_populates="lich_su_kiem_ke")
    """ Các bản ghi kiểm kê cho phòng đó """

# Define the association table for the many-to-many relationship
ban_ghi_kiem_ke_tai_san_association = Table(
    'ban_ghi_kiem_ke_tai_san',
    Base.metadata,
    Column('trang_thai', String(length=255)),  # Additional attribute for the relationship
    Column('tai_san_id', Integer, ForeignKey('tai_san.id')),
    Column('ban_ghi_kiem_ke_id', Integer, ForeignKey('ban_ghi_kiem_ke.id')),
)

class BanGhiKiemKe(Base):
    __tablename__ = "ban_ghi_kiem_ke"
    id = Column(Integer, primary_key=True, autoincrement=True)
    thoi_gian = Column(DateTime, default=datetime.utcnow())
    """ Thời gian kiểm kê xong """
    # 1-n relationships
    # n-1 relationships
    lich_su_kiem_ke_id = Column(Integer, ForeignKey('lich_su_kiem_ke.id'))
    lich_su_kiem_ke = relationship("LichSuKiemKe", back_populates="ban_ghi_kiem_kes")
    # n-n relationships
    tai_sans = relationship("TaiSan", secondary=ban_ghi_kiem_ke_tai_san_association, back_populates="ban_ghi_kiem_kes")

"""
class BanGhiKiemKe_TaiSan(Base):
    __tablename__ = "ban_ghi_kiem_ke_tai_san"
    tai_san_id = Column(Integer, ForeignKey('tai_san.id'), primary_key=True)
    trang_thai = Column(String(length=255))  # Additional attribute for the relationship
    ban_ghi_kiem_ke_id = Column(Integer, ForeignKey('ban_ghi_kiem_ke.id'), primary_key=True)
    tai_san = relationship("TaiSan", back_populates="ban_ghi_kiem_ke_tai_san")
    ban_ghi_kiem_ke = relationship("BanGhiKiemKe", back_populates="ban_ghi_kiem_ke_tai_san")
"""
class TaiSan(Base):
    __tablename__ = "tai_san"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # ten = Column(String(length=255), nullable=True, unique=False)  # Có nhiều tài sản cùng tên (VD Tivi LG, Tivi LG)
    # ma_phan_loai = ma_don_vi.ma_phong.ma_loai_tai_san
    ma = Column(String(length=255), nullable=False, unique=False)   # Có nhiều tài sản cùng mã
    # ma_dinh_danh = ma_phan_loai.ma_tai_san
    ma_serial = Column(String(length=255))
    mo_ta = Column(String(length=255))
    nam_su_dung = Column(String(length=255))
    ghi_chu = Column(String(length=255))
    # 1-n relationships
    # n-1 Relationships
    loai_tai_san_id = Column(Integer, ForeignKey('loai_tai_san.id'))
    loai_tai_san = relationship('LoaiTaiSan', back_populates='tai_sans')
    phong_id = Column(Integer, ForeignKey('phong.id'))
    phong = relationship("Phong", back_populates="tai_sans")
    # n-n relationships
    ban_ghi_kiem_kes = relationship("BanGhiKiemKe", secondary=ban_ghi_kiem_ke_tai_san_association, back_populates="tai_sans")

"""
# One-to-one
class Citizen(Base):
    __tablename__ = "citizen"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    # Relationships
    passport = relationship("Passport")

class Passport(Base):
    __tablename__ = "passport"
    id = Column(Integer, primary_key=True)
    citizen_id = Column(Integer, ForeignKey("citizen.id"))
    passport_id = Column(String(25), unique=True, nullable=False)
    # Relationships
    citizen = relationship("Citizen")

# One-to-many
class Customer(Base):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    orders = relationship("Order", back_populates="customer")

class Order(Base):
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer.id'))

    # Relationship
    customer = relationship("Customer", back_populates="orders")

# For example, to get the orders for a customer, we can write:
customer = session.query(Customer).get(1)
orders = customer.orders

# For example, to get the customer for an order, we can write:
order = session.query(Order).get(1)
customer = order.customer

Many-to-many
class Student(Base):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # Relationship
    courses = relationship("Course", secondary="student_course", back_populates="students")

class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # Relationship
    students = relationship("Student", secondary="student_course", back_populates="courses")

class StudentCourse(Base):
    __tablename__ = 'student_course'
    student_id = Column(Integer, ForeignKey('student.id'), primary_key=True)
    course_id = Column(Integer, ForeignKey('course.id'), primary_key=True)

# For example, to get the courses for a student, we can write:
student = session.query(Student).get(1)
courses = student.courses
"""

"""
Sure! Here are some examples of how you can perform CRUD operations on the Users and Clients models with the many-to-many relationship:

Create a new user and associate it with one or more clients:
python
Copy code
# Create a new user
new_user = Users(username='john', password='password123', role='admin')

# Add clients to the user's clients list
client1 = Clients(id=b'client1')
client2 = Clients(id=b'client2')
new_user.clients.extend([client1, client2])

# Add the user to the session and commit the changes
session.add(new_user)
session.commit()
Get all clients associated with a specific user:
python
Copy code
# Get a specific user by username
user = session.query(Users).filter_by(username='john').first()

# Access the associated clients using the clients attribute
clients = user.clients
for client in clients:
    print(client.id)
Add a new client and associate it with one or more existing users:
python
Copy code
# Create a new client
new_client = Clients(id=b'client3')

# Get existing users
users = session.query(Users).filter(Users.username.in_(['john', 'alice'])).all()

# Add the new client to each user's clients list
for user in users:
    user.clients.append(new_client)

# Commit the changes
session.commit()
Remove a client from a user's clients list:
python
Copy code
# Get a specific user by username
user = session.query(Users).filter_by(username='john').first()

# Remove a client from the user's clients list
client_to_remove = session.query(Clients).filter_by(id=b'client1').first()
user.clients.remove(client_to_remove)

# Commit the changes
session.commit()
Delete a user and automatically remove the association with clients:
python
Copy code
# Get a specific user by username
user = session.query(Users).filter_by(username='john').first()

# Delete the user
session.delete(user)

# Commit the changes
session.commit()
These examples demonstrate how to create, read, update, and delete data in the Users and Clients models while maintaining the many-to-many relationship.
"""