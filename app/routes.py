from flask import Flask, render_template, request, flash, redirect, url_for, Response, abort
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from app.forms import LoginForm
from functools import wraps
from app import app, db
from app.custom_decor import whitelisted
import datetime, time
import math
from app.models import User, Role, UserRoles,\
    Regions, RegionAttributes, CityAttributes,\
    UserAttributes, SkillTracker, RegionWar,\
    Articles

loginMgr = LoginManager()


@app.route('/')
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        if not request.form['username'] or not request.form['password'] or not request.form['email']:
            flash('All fields are required or you failed the captcha', 'error')
            return render_template('register.html', title="User Registration")
        elif request.form['username'] and request.form['password'] and request.form['email']:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            user = User(username, password, email)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('show_all'))


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    article = Articles.query.join(User, User.id == Articles.user).add_columns(Articles.id,
                                                                              Articles.user,
                                                                              Articles.timesubmit,
                                                                              Articles.timeupdate,
                                                                              Articles.content,
                                                                              User.username).all()
    return render_template('user.html', user=user, posts=article, title="User Profile {}".format(user.username))


@app.route('/article/<id>')
@login_required
def article(id):
    if id == int:
        articles = Articles.query.join(User, User.id == Articles.user).add_columns(Articles.id,
                                                                               Articles.title,
                                                                               Articles.user,
                                                                               Articles.timesubmit,
                                                                               Articles.timeupdate,
                                                                               Articles.content,
                                                                               User.username).filter_by(id=id)
        return render_template('article.html', posts=articles)
    if id == 'new':
        return render_template('article.html', new=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('show_all'))
        form = LoginForm()
        return render_template('new.html', form=form)
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        user = User.query.filter_by(username=form.username.data).first()
        print(form.username.data)
        if user.check_password(form.password.data) is True:
            login_user(user)
        return redirect(url_for('show_all'))
    return render_template('new.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')


@app.route('/explore')
@app.route('/explore/<page>')
@login_required
def explore(page=None):
    if page == None:
        page = 1
    per_page = 20
    regions = Regions.query.join(RegionAttributes,
                                 Regions.id == RegionAttributes.id).add_columns(Regions.id,
                                                                                Regions.name,
                                                                                Regions.colour,
                                                                                Regions.file,
                                                                                RegionAttributes.attack,
                                                                                RegionAttributes.defense,
                                                                                RegionAttributes.hasBarracks,
                                                                                RegionAttributes.hasHumanOwner).order_by(Regions.id).paginate(int(page), per_page, False)

    lastpage = math.ceil(regions.total/per_page)
    prev_url = url_for('explore',page=regions.next_num) \
        if regions.has_next else 1
    next_url = url_for('explore',page=regions.prev_num) \
        if regions.has_prev else lastpage
    return render_template("region_list.html", title='Explore', regions=regions.items, user=current_user,
                           next_url=next_url, prev_url=prev_url)


@app.route('/map')
#@whitelisted
@login_required
def show_all():
    #print(request.headers)
    record = SkillTracker.query.filter_by(userid=current_user.id).first()
    if record != None:
        tr = time.strftime('%d/%m/%Y - %H:%M:%S', time.localtime(record.timecomplete))
    else:
        tr = None
    j = Regions.query.join(RegionAttributes,
                           Regions.id == RegionAttributes.id).add_columns(Regions.id,
                                                                          Regions.name,
                                                                          Regions.colour,
                                                                          Regions.file,
                                                                          RegionAttributes.attack,
                                                                          RegionAttributes.defense,
                                                                          RegionAttributes.hasBarracks,
                                                                          RegionAttributes.hasHumanOwner)
    ua = UserAttributes.query.filter_by(user_id=current_user.id).first()
    activewars = RegionWar.query.filter_by(isactive=1).all()
    city_attr = CityAttributes.query.all()
    return render_template('show_all.html', regions = j, user=current_user, ua=ua, tr=tr, wars=activewars, ca=city_attr)

@app.route('/war')
@app.route('/war/<page>')
@login_required
def allwars(page=None):
    if page == None:
        page = 1
    per_page = 10
    wars = RegionWar.query.paginate(page, per_page, False)
    lastpage = math.ceil(wars.total / per_page)
    prev_url = url_for('explore', page=wars.next_num) \
        if wars.has_next else 1
    next_url = url_for('explore', page=wars.prev_num) \
        if wars.has_prev else lastpage

    return render_template('playerwar.html', wars=wars, user=current_user, prev_url=prev_url, next_url=next_url)


@app.route('/war/fight/<id>')
@login_required
def playerwar(id):
    if id == None:
        return(url_for('war'))

    if id != None:
        war = RegionWar.query.filter_by(id=id).first_or_404()
        offregion = CityAttributes.query.filter_by(id=war.regionida).first()
        defregion = CityAttributes.query.filter_by(id=war.regionidd).first()
        return render_template('playerwar.html', offense=offregion, defense=defregion, war=war, user=current_user)



@app.route('/action', methods=['POST'])
@app.route('/action/<api_name>', methods=['POST'])
@login_required
def action(api_name):
    if api_name == 'attack':
        if request.method == 'POST':
            if not request.form['regionA'] or not request.form['regionD']:
                flash('Please enter all the fields', 'error')
            else:
                regiona = request.form['regionA']
                regiond = request.form['regionD']
                citya = CityAttributes.query.filter_by(name=regiona).first()
                cityd = CityAttributes.query.filter_by(name=regiond).first()
                RegionA = Regions.query.filter_by(name=regiona).join(RegionAttributes,
                                                                     Regions.id == RegionAttributes.id).add_columns(RegionAttributes.attack,
                                                                                                                    RegionAttributes.defense,
                                                                                                                    RegionAttributes.hasBarracks).first()
                RegionD = Regions.query.filter_by(name=regiond).join(RegionAttributes,
                                                                     Regions.id == RegionAttributes.id).add_columns(RegionAttributes.attack,
                                                                                                                    RegionAttributes.defense,
                                                                                                                    RegionAttributes.hasBarracks).first()
                war = RegionWar(citya.id, cityd.id, RegionA.attack, RegionD.defense)
                db.session.add(war)
                db.session.commit()
                #flash('War is: {}<br>{} {} {} {}'.format(war, citya.id, cityd.id, RegionA.attack, RegionD.defense))
                #db.session.add(war)
                try:
                    distance = [math.fabs(citya.x - cityd.x),
                                math.fabs(citya.y - cityd.y)]
                except AttributeError as e:
                    flash('Problem with attack move API: {} | {}'.format(e, (citya, cityd)), 'error')
                    return render_template('show_all.html')
                distance = (distance[0] + distance[1]) / 2
                if distance <= 250:
                    offPower = RegionA.attack + (RegionA.attack * 0.21)
                    defPower = RegionD.defense
                    flash(str(offPower) + '|' + str(defPower))
                    if RegionA.hasBarracks == 1:
                        offPower = offPower * 0.21
                    if RegionD.hasBarracks == 1:
                        defPower = defPower * 0.21

                    if offPower > defPower:
                        timeTag = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
                        flash('<h2>War results {} vs. {} at {}</h2><p>Attack successful at range of {}<p>'.format(
                            cityd.name, cityd.name, timeTag, distance))
                        defender = Regions.query.get(RegionD.Regions.id)
                        newColour = RegionA.Regions.colour
                        defender.colour = newColour
                        db.session.commit()
                else:

                    flash('<h2>War failed<h2><p>Bad attack move -- Distance {} is greater than 250 miles</p>'.format(
                        math.floor(distance)))

            return redirect(url_for('show_all'))
    else:
        return '<h3>Not allowed</h3>'


@app.route('/train', methods=['POST'])
@app.route('/train/<api_name>', methods=['POST'])
@login_required
def train(api_name):
    if api_name == 'intelligence':
        track = SkillTracker.query.filter_by(userid=current_user.id, isactive=1).all()
        if track == []:
            upgrade = SkillTracker(current_user.id, 'int', UserAttributes.query.filter_by(user_id=current_user.id).first().intelligence)
            db.session.add(upgrade)
            db.session.commit()
            return redirect(url_for('show_all'))
        else:
            flash('You\'re already upgrading a skill at the moment...')
            return redirect(url_for('show_all'))
    if api_name == 'endurance':
        track = SkillTracker.query.filter_by(userid=current_user.id, isactive=1).all()
        if track == []:
            upgrade = SkillTracker(current_user.id, 'end',
                                   UserAttributes.query.filter_by(user_id=current_user.id).first().endurance)
            db.session.add(upgrade)
            db.session.commit()
            return redirect(url_for('show_all'))
        else:
            flash('You\'re already upgrading a skill at the moment...')
            return redirect(url_for('show_all'))
    if api_name == 'strength':
        track = SkillTracker.query.filter_by(userid=current_user.id, isactive=1).all()
        if track == []:
            upgrade = SkillTracker(current_user.id, 'str',
                                   UserAttributes.query.filter_by(user_id=current_user.id).first().strength)
            db.session.add(upgrade)
            db.session.commit()
            return redirect(url_for('show_all'))
        else:
            flash('You\'re already upgrading a skill at the moment...')
            return redirect(url_for('show_all'))


@loginMgr.user_loader
def load_user(id):
    return User.query.get(int(id))