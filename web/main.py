from datetime import datetime
import timeago
from flask import Flask, render_template, request
from sqlalchemy.exc import DatabaseError
from fedora_review_service.database import (
    Ticket,
    Build,
    Message,
    session,
)
from fedora_review_service.logic.copr import copr_build_url

# We should move this into config
DATAGREPPER = "https://apps.fedoraproject.org/datagrepper/v2"

app = Flask(__name__)


def datagrepper_topic_url(topic):
    return "{0}/search?topic={1}".format(DATAGREPPER, topic)


def datagrepper_message_url(message):
    url = "{0}/id?id={1}&is_raw=true&size=extra-large"
    return url.format(DATAGREPPER, message)


@app.template_filter("timeago")
def human_friendly_time_ago(date):
    return timeago.format(date, datetime.now())


@app.context_processor
def jinja2_global_functions():
    return {
        "datagrepper_topic_url": datagrepper_topic_url,
        "datagrepper_message_url": datagrepper_message_url,
        "copr_build_url": copr_build_url,
    }


@app.errorhandler(DatabaseError)
def handle_error(ex):
    return render_template("error.html", message=ex)


@app.route("/")
def homepage():
    return render_template("index.html")


@app.route("/messages")
def get_messages():
    messages = (
        session.query(Message)
        .order_by(Message.id.desc())
        .limit(10)
        .all()
    )
    max_id = messages[0].id
    min_id = messages[-1].id
    return render_template("messages.html", messages=messages,
                           min_id=min_id, max_id=max_id)


@app.route("/htmx/messages/")
def htmx_get_messages():
    max_id = request.args.get("max_id", None)
    min_id = request.args.get("min_id", None)

    query = session.query(Message).order_by(Message.id.desc())
    if max_id:
        query = query.filter(Message.id > max_id)
    elif min_id:
        query = query.filter(Message.id < min_id).limit(10)
    else:
        raise NotImplementedError

    messages = query.all()
    max_id = messages[0].id if messages else max_id
    min_id = messages[-1].id if messages else min_id
    return render_template("htmx_messages.html", messages=messages,
                           min_id=min_id, max_id=max_id)


@app.route("/tickets")
def get_tickets():
    tickets = (
        session.query(Ticket)
        .order_by(Ticket.rhbz_id.desc())
        .limit(300)
        .all()
    )
    max_id = tickets[0].rhbz_id
    min_id = tickets[-1].rhbz_id
    return render_template("tickets.html", tickets=tickets,
                           min_id=min_id, max_id=max_id)


@app.route("/htmx/tickets/")
def htmx_get_tickets():
    max_id = request.args.get("max_id", None)
    min_id = request.args.get("min_id", None)

    query = session.query(Ticket).order_by(Ticket.rhbz_id.desc())
    if max_id:
        query = query.filter(Ticket.rhbz_id > max_id)
    elif min_id:
        query = query.filter(Ticket.rhbz_id < min_id).limit(300)
    else:
        raise NotImplementedError

    tickets = query.all()
    max_id = tickets[0].rhbz_id if tickets else max_id
    min_id = tickets[-1].rhbz_id if tickets else min_id
    return render_template("htmx_tickets.html", tickets=tickets,
                           min_id=min_id, max_id=max_id)


@app.route("/ticket/<int:rhbz_id>")
def get_ticket(rhbz_id):
    ticket = session.query(Ticket).filter(Ticket.rhbz_id == rhbz_id).one()
    ticket.builds.sort(key=lambda x: x.id, reverse=True)
    max_id = ticket.builds[0].id
    min_id = ticket.builds[-1].id
    return render_template("ticket.html", ticket=ticket,
                           min_id=min_id, max_id=max_id)


@app.route("/htmx/ticket/<int:rhbz_id>/")
def htmx_get_ticket(rhbz_id):
    max_id = request.args.get("max_id", None)
    min_id = request.args.get("min_id", None)

    query = (
        session.query(Build)
        .join(Build.ticket)
        .filter(Ticket.rhbz_id == rhbz_id)
        .order_by(Build.id.desc())
    )
    if max_id:
        query = query.filter(Build.id > max_id)
    elif min_id:
        query = query.filter(Build.id < min_id).limit(1)
    else:
        raise NotImplementedError

    builds = query.all()
    max_id = builds[0].id if builds else max_id
    min_id = builds[-1].id if builds else min_id
    return render_template("htmx_ticket.html", builds=builds, rhbz_id=rhbz_id,
                           min_id=min_id, max_id=max_id)


@app.route("/builds")
def get_builds():
    builds = (
        session.query(Build)
        .filter(Build.copr_build_id.is_not(None))
        .order_by(Build.copr_build_id.desc())
        .limit(300)
        .all()
    )
    max_id = builds[0].copr_build_id
    min_id = builds[-1].copr_build_id
    return render_template("builds.html", builds=builds,
                           min_id=min_id, max_id=max_id)


@app.route("/htmx/builds/")
def htmx_get_builds():
    max_id = request.args.get("max_id", None)
    min_id = request.args.get("min_id", None)

    query = session.query(Build).order_by(Build.copr_build_id.desc())
    if max_id:
        query = query.filter(Build.copr_build_id > max_id)
    elif min_id:
        query = query.filter(Build.copr_build_id < min_id).limit(300)
    else:
        raise NotImplementedError

    builds = query.all()
    max_id = builds[0].copr_build_id if builds else max_id
    min_id = builds[-1].copr_build_id if builds else min_id
    return render_template("htmx_builds.html", builds=builds,
                           min_id=min_id, max_id=max_id)
