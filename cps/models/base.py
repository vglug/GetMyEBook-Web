try:
    # Compatibility with sqlalchemy 2.0
    from sqlalchemy.orm import declarative_base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    

Base = declarative_base()
calibre_Base = declarative_base()