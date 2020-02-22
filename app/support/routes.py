from flask import flash, redirect, render_template, url_for
from flask_babel import gettext as _
from flask_login import login_required, current_user

from app import db
from app.models import Ticket
from app.support import bp
from app.support.forms import SupportForm
from app.utils.decorators import check_confirmed


@bp.route('/support/create_ticket', methods=['GET', 'POST'])
@login_required
@check_confirmed
def create_ticket():
    form = SupportForm()
    if form.validate_on_submit():
        ticket = Ticket(body=form.message.data, author=current_user)
        db.session.add(ticket)
        db.session.commit()
        flash(_('Thanks for contributing the issue. You ticket has been submitted!'))
        return redirect(url_for('tips.get_tip'))
    return render_template('support/new_ticket.html', title='Create new ticket', form=form)
