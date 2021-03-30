import sqlite3
from typing import List
from vesna.googleparser import DetainedInfo

class WFDatabase:
    conn = None

    def __init__(self, dbUrl):
        self.conn = sqlite3.connect(dbUrl)

    def findOverlap (self, detainedList: List[DetainedInfo]) -> List[DetainedInfo]:
        result = []
        c = self.conn.cursor();
        for detained in detainedList:
            fullName = detained.name.split()
            matches = []
            if len(fullName) > 1:
                matches = c.execute(
                    "SELECT * FROM employees WHERE first_name=? and last_name=? and status != 'NOTIFIED'", (fullName[0], fullName[1],)).fetchall()
            else:
                matches = c.execute(
                    "SELECT * FROM employees WHERE first_name=? and status != 'NOTIFIED'", (fullName[0],)).fetchall()

            if matches:
                detained.id = matches[0][0]
                detained.wfName = " ".join(matches[0][1:4])
                result.append(detained)


        self.conn.commit()
        return result

    def markDetained(self, detained):
        c = self.conn.cursor();
        c.execute("UPDATE employees SET status='NOTIFIED' WHERE id=?", (detained.id,))
        self.conn.commit()

    def resetState(self):
        c = self.conn.cursor();
        c.execute("UPDATE employees SET status=''")
        self.conn.commit()


