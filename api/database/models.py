import enum
from sqlalchemy import Column, Integer, String, func, ForeignKey, Boolean, Table, Numeric
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy_utils import aggregated


Base = declarative_base()


class RoleNames(enum.Enum):
    admin: str = 'admin'
    moderator: str = 'moderator'
    user: str = 'user'

    @staticmethod
    def get_max_role_len():
        return len(max(list(RoleNames.__members__), key=lambda item: len(item)))


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(RoleNames.get_max_role_len()), default=RoleNames.user)
    can_post_own_pict = Column(Boolean, default=True)
    can_del_own_pict = Column(Boolean, default=True)
    can_mod_own_pict = Column(Boolean, default=True)

    can_post_own_comment = Column(Boolean, default=True)
    can_mod_own_comment = Column(Boolean, default=True)
    can_del_own_comment = Column(Boolean, default=False)

    can_post_tag = Column(Boolean, default=True)
    can_mod_tag = Column(Boolean, default=False)
    can_del_tag = Column(Boolean, default=False)

    can_post_not_own_pict = Column(Boolean, default=False)
    can_mod_not_own_pict = Column(Boolean, default=False)
    can_del_not_own_pict = Column(Boolean, default=False)

    can_post_not_own_comment = Column(Boolean, default=False)
    can_mod_not_own_comment = Column(Boolean, default=False)
    can_del_not_own_comment = Column(Boolean, default=False)

    can_change_user_role = Column(Boolean, default=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100))
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    role_id = Column(Integer, ForeignKey(Role.id))
    confirmed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    slug = Column(String(255), unique=True, nullable=False)
    avatar = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    role = relationship("Role", backref="users")


picture_m2m_tag = Table(
    "picture_m2m_tag",
    Base.metadata,
    Column("picture_id", Integer, ForeignKey("pictures.id", ondelete="CASCADE"), nullable=False),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False),
    UniqueConstraint('picture_id', 'tag_id', name='pic_tag_uniq')
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Picture(Base):
    __tablename__ = "pictures"

    id = Column(Integer, primary_key=True)
    picture_url = Column(String(1024))
    description = Column(String(10000))
    user_id = Column('user_id', Integer, ForeignKey('users.id', ondelete="CASCADE"))
    shared = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    update = Column(Boolean, default=False)
    tags = relationship("Tag", secondary=picture_m2m_tag, backref="pictures")
    user = relationship("User", backref="pictures")

    @aggregated('rating', Column(Numeric))
    def avg_rating(self):
        return func.avg(Rating.rate)
    
    rating = relationship('Rating')
   

class TransformedPicture(Base):
    __tablename__ = 'transformed_pictures'
    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    picture_id = Column(Integer, ForeignKey(Picture.id, ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    picture = relationship('Picture', backref="transformed_pictures")
    UniqueConstraint('picture_id', 'url', name='pic_trans_url_uniq')


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    text = Column(String(10000))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    picture_id = Column(Integer, ForeignKey(Picture.id, ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship('User', backref="comments")
    picture = relationship('Picture', backref="comments")
    edited = Column(Boolean, default=False)  # Поле, яке вказує, чи був коментар редагований
    edited_at = Column(DateTime, nullable=True)  # Поле, яке зберігає час останнього редагування коментаря


class BlacklistToken(Base):
    __tablename__ = 'blacklist_tokens'

    id = Column(Integer, primary_key=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    blacklisted_on = Column(DateTime, default=func.now())


class Rating(Base):
    __tablename__ = 'rating'

    id = Column(Integer, primary_key=True)
    picture_id = Column('picture_id', ForeignKey(Picture.id, ondelete='CASCADE'), nullable=False)
    rate = Column(Integer, default=0)
    user_id: int = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    created_at = Column(DateTime, default=func.now())

    user = relationship('User', backref="rating")
