# coding = utf-8
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship, backref
from datetime import datetime
import enum

from db import Base, engine


class EvaluationRecord(Base):
    """评估记录表单"""

    __tablename__ = 'evaluation_record'

    id = Column(Integer, primary_key=True, autoincrement=True, doc='序号')
    uuid = Column(String, nullable=False, doc='uuid')  # 设置非空且唯一
    count = Column(Integer, default=0, doc='测评次数')
    create_time = Column(DateTime, default=datetime.now, doc='创建时间')
    name = Column(String, nullable=False, index=True, doc='系统名称')
    level = Column(Integer, nullable=False, doc='安全保护等级')  # 2为第二等级，3为第三等级
    devices_address = Column(String, nullable=False, doc='安全设备地址列表')
    address = Column(String, nullable=False, doc='业务系统地址列表')
    status = Column(Enum("waiting", "evaluating", "finished",
                         "cancel", "failure"), default="waiting", doc='评估状态')
    non_compliance = Column(Integer, default=0, doc='不合规项数量')
    high_risk = Column(Integer, default=0, doc='高风险项')
    is_delete = Column(Boolean, default=False, doc='逻辑删除')


class EvaluationItems(Base):
    """测评项目"""

    __tablename__ = 'evaluation_items'

    id = Column(Integer, primary_key=True, autoincrement=True, doc='序号')
    evaluation_id = Column(Integer, ForeignKey(
        EvaluationRecord.id), doc='评估记录id')
    eval = Column(String, nullable=False, doc='测评项编号')
    device = Column(String, doc='设备名称')
    device_address = Column(String, doc='设备地址')
    device_id = Column(String, doc='设备id')
    conformity = Column(Integer, doc='符合状态')   # 1 -> 符合, 2 -> 部分符合, 3 -> 不符合
    compliance_ability = Column(String, doc='满足详情')
    advice = Column(String, doc='整改建议')
    is_check = Column(Boolean, default=False, doc='核查确认')
    check_explain = Column(String, doc='核查确认说明')
    item = Column(String, doc='子项')
    kind = Column(Enum("configuration", "global", "artificial"),
                  default=None, doc='待处理事项类别')
    evaluation = relationship("EvaluationRecord", backref="evaluation_items")


class OperationRecord(Base):
    """操作记录"""

    __tablename__ = 'operation_record'

    id = Column(Integer, primary_key=True, autoincrement=True, doc='序号')
    operation_time = Column(DateTime, default=datetime.now, doc='操作时间')
    evaluation_id = Column(Integer, ForeignKey(
        EvaluationRecord.id), doc='评估记录id')
    evaluation_items_id = Column(
        Integer, ForeignKey(EvaluationItems.id), doc='评估项记录ID')
    operation = Column(Enum("create", "update", "delete"),
                       nullable=False, doc='操作')
    operation_field = Column(String, doc='操作字段')
    old_content = Column(String, doc='旧值')
    new_content = Column(String, doc='新值')
    evaluation = relationship("EvaluationRecord", backref="operation_record")
    evaluation_items = relationship(
        "EvaluationItems", backref="operation_record")


class SystemInfor(Base):
    """业务系统基础情况"""

    __tablename__ = 'system_infor'

    id = Column(Integer, primary_key=True, autoincrement=True, doc='序号')
    evaluation_id = Column(Integer, ForeignKey(
        EvaluationRecord.id), doc='评估记录id')
    is_net = Column(Boolean, default=False, doc='是否对互联网提供服务')
    is_sub_organ = Column(Boolean, default=False, doc='是否对下属机构提供服务')
    is_spam = Column(Boolean, default=False, doc='是否和垃圾邮件网关/系统相关')
    is_gateway = Column(Boolean, default=False, doc='是否和无线网关控制器相关')
    is_vpn = Column(Boolean, default=False, doc='是否支持SSL VPN远程访问')
    evaluation = relationship("EvaluationRecord", backref="system_infor")


class DevicesTag(Base):
    """设备标志"""

    __tablename__ = "devices_tag"

    id = Column(Integer, primary_key=True, autoincrement=True, doc='序号')
    device_id = Column(String, nullable=False, doc='设备id')
    name = Column(String, nullable=False, doc='设备名称')
    tag = Column(String, doc='设备标志')
    address = Column(String, nullable=False, doc='设备IP地址')


Base.metadata.create_all(engine)
