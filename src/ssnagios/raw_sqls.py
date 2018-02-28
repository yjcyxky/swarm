import logging
from django.db import connection, transaction
from django.db.utils import ProgrammingError

logger = logging.getLogger(__file__)


def add_fields():
    raw_sqls = (
        "ALTER TABLE `nagios_notifications` add `checked` tinyint(1) NOT NULL default '0'",
        "ALTER TABLE `nagios_notifications` add `checked_time` datetime NOT NULL default '1990-01-01 00:00:00'"
    )
    cursor = connection.cursor()
    try:
        for sql in raw_sqls:
            cursor.execute(sql)
    except ProgrammingError as err:
        logger.error("nagios_notifications table doesn't exist.\n"
                     "Please install ndoutils following 'https://support.nagios.com/kb/article/ndoutils-installing-ndoutils-406.html'")
        logger.debug(str(err))
    transaction.commit()
