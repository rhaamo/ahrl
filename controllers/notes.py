from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_security import login_required, current_user
from sqlalchemy import func

from forms import NoteForm
from models import db, Note, Logbook, Log
from utils import check_default_profile

bp_notes = Blueprint("bp_notes", __name__)


@bp_notes.route("/notes", methods=["GET"])
@login_required
@check_default_profile
def notes():
    pcfg = {"title": "My notes"}

    _notes = Note.query.filter(Note.user_id == current_user.id).all()
    logbooks = (
        db.session.query(Logbook.id, Logbook.name, func.count(Log.id))
        .join(Log)
        .filter(Logbook.user_id == current_user.id)
        .group_by(Logbook.id)
        .all()
    )

    return render_template("notes/view.jinja2", pcfg=pcfg, notes=_notes, logbooks=logbooks)


@bp_notes.route("/notes/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
@check_default_profile
def edit(note_id):
    pcfg = {"title": "Edit my notes"}

    a = Note.query.filter(Note.user_id == current_user.id, Note.id == note_id).first()
    if not a:
        flash("Note not found", "error")
        return redirect(url_for("bp_notes.notes"))

    form = NoteForm(request.form, obj=a)

    if form.validate_on_submit():
        a.title = form.title.data
        a.cat = form.cat.data
        a.note = form.note.data

        db.session.commit()

        flash("Success saving note: {0}".format(a.title), "success")
        return redirect(url_for("bp_notes.notes"))

    logbooks = Logbook.query.filter(Logbook.user_id == current_user.id).all()

    return render_template("notes/edit.jinja2", pcfg=pcfg, form=form, note=a, note_id=note_id, logbooks=logbooks)


@bp_notes.route("/notes/new", methods=["GET", "POST"])
@login_required
@check_default_profile
def new():
    pcfg = {"title": "New note"}

    form = NoteForm()

    if form.validate_on_submit():
        a = Note()
        a.title = form.title.data
        a.cat = form.cat.data
        a.note = form.note.data
        a.user_id = current_user.id

        db.session.add(a)
        db.session.commit()

        flash("Success updating note: {0}".format(a.title), "success")
        return redirect(url_for("bp_notes.notes"))

    logbooks = (
        db.session.query(Logbook.id, Logbook.name, func.count(Log.id))
        .join(Log)
        .filter(Logbook.user_id == current_user.id)
        .group_by(Logbook.id)
        .all()
    )
    return render_template("notes/new.jinja2", pcfg=pcfg, form=form, logbooks=logbooks)


@bp_notes.route("/notes/<int:note_id>/delete", methods=["GET", "DELETE", "PUT"])
@login_required
@check_default_profile
def delete(note_id):
    note = Note.query.filter(Note.user_id == current_user.id, Note.id == note_id).first()
    if not note:
        flash("Note not found", "error")
        return redirect(url_for("bp_notes.notes"))

    db.session.delete(note)
    db.session.commit()

    return redirect(url_for("bp_notes.notes"))
