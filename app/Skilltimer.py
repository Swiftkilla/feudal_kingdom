import threading
from app.models import SkillTracker, UserAttributes, SkillHistory, RegionWar, DamageWar
from flask_sqlalchemy import SQLAlchemy
from app import db
import time, math

class SkillTimer(threading.Thread, SkillTracker):
    def __init__(self, SkillTracker=SkillTracker):
        threading.Thread.__init__(self)
        self.skillcheck = SkillTracker.query.filter_by(isactive=1).all()
        self.skillclean = SkillTracker.query.filter_by(isactive=0).all()
    def run(self):
        while True:
            # for x in range(1,30+1):
            #     print(x)
            time.sleep(5)
            self.skillcheck = SkillTracker.query.filter_by(isactive=1).all()
            self.skillclean = SkillTracker.query.filter_by(isactive=0).all()

            if self.skillcheck != []:
                print(self.skillcheck)
                for record in self.skillcheck:
                    print('IS RECORD ACTIVE: {}'.format(record.isactive))
                    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.timecomplete)))
                    if record.isactive == 1:
                        if record.timesubmit + record.timetowait <= time.time():
                            user = UserAttributes.query.filter_by(user_id=record.userid).first()
                            if record.targetskill == 'int':
                                record.isactive = 0
                                user.intelligence += 1
                                db.session.commit()
                                print('User {} upgraded {}, level = {} -- {}'.format(user.user_id, record.targetskill,
                                                                                     user.intelligence, time.time()))
                            if record.targetskill == 'end':
                                record.isactive = 0
                                user.endurance += 1
                                db.session.commit()
                                print('User {} upgraded {}, level = {} -- {}'.format(user.user_id, record.targetskill,
                                                                                     user.endurance, time.time()))
                            if record.targetskill == 'str':
                                record.isactive = 0
                                user.strength += 1
                                db.session.commit()
                                print('User {} upgraded {}, level = {} -- {}'.format(user.user_id, record.targetskill,
                                                                                     user.strength, time.time()))
                            self.skillcheck.remove(record)

                self.skillcheck = SkillTracker.query.filter_by(isactive=0).all()

            if self.skillcheck == []:
                print(time.strftime('Nothing to do --- %H:%M:%S %Y-%M-%D ', time.localtime(time.time())))

            if self.skillclean != []:
                for record in self.skillclean:
                    if record.isactive == 0:
                        print(record)
                        skillhistory = SkillHistory(record.userid, record.targetskill,
                                                    record.timesubmit, record.timetowait, record.timecomplete)
                        db.session.add(skillhistory)
                        db.session.delete(record)
                        db.session.commit()
                        self.skillclean.remove(record)

                self.skillclean = SkillTracker.query.filter_by(isactive=0).all()
            else:
                print(time.strftime('No old records --- %H:%M:%S %Y-%M-%D ', time.localtime(time.time())))

class WarTimer(threading.Thread, RegionWar):
    def __init__(self, WarTracker=RegionWar):
        threading.Thread.__init__(self)
        self.warcheck = WarTimer.query.filter_by(isactive=1).all()
        self.warclean = WarTimer.query.filter_by(isactive=0).all()

    def run(self):
        while True:
            # for x in range(1,30+1):
            #     print(x)
            time.sleep(5)
            self.warcheck = SkillTracker.query.filter_by(isactive=1).all()
            self.warclean = SkillTracker.query.filter_by(isactive=0).all()


skilltime = SkillTimer()
skilltime.run()
#skilltimer.run()