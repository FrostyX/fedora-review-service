from unittest.mock import patch
from tests.base import MessageTestCase
from fedora_review_service.consumer import (
    handle_copr_message,
    handle_bugzilla_message,
)
from fedora_review_service.database import create_db, Ticket, Build, Message, session, Base, engine


class TestConsumer(MessageTestCase):
    def setUp(self):
        super().setUp()
        create_db()

    def tearDown(self):
        session.rollback()
        for tbl in reversed(Base.metadata.sorted_tables):
            engine.execute(tbl.delete())

    @patch("fedora_review_service.consumer.submit_to_copr")
    def test_handle_bugzilla_message(self, submit_to_copr):
        submit_to_copr.return_value = 123

        message = self.get_message("bugzilla-contributor-srpm-update.json")
        handle_bugzilla_message(message)

        msgobj = session.query(Message).one()
        assert msgobj.done is True
        assert msgobj.topic == "org.fedoraproject.prod.bugzilla.bug.update"

        ticket = session.query(Ticket).one()
        assert ticket.rhbz_id == 2120131
        assert ticket.owner == "ales.astone@gmail.com"

        build = session.query(Build).one()
        assert build.copr_build_id == 123
        assert build.bugzilla_message_id == msgobj.id
        assert build.ticket_id == 1
        assert build.spec_url.endswith("libgbinder.spec")
        assert build.srpm_url.endswith("libgbinder-1.1.29-1.fc38.src.rpm")

    @patch("fedora_review_service.consumer.submit_to_copr")
    @patch("fedora_review_service.consumer.submit_bugzilla_comment")
    @patch("fedora_review_service.consumer.upload_bugzilla_patch")
    def test_handle_copr_message(self, upload_bugzilla_patch,
                                 submit_bugzilla_comment, submit_to_copr):
        submit_to_copr.return_value = 5069760
        message = self.get_message("bugzilla-contributor-srpm-update.json")
        handle_bugzilla_message(message)

        # And now handle the corresponding Copr message
        message = self.get_message("copr-review-build-end.json")
        handle_copr_message(message)

        msgobj = session.query(Message).order_by(Message.id.desc()).first()
        assert msgobj.topic == "org.fedoraproject.prod.copr.build.end"

        build = session.query(Build).one()
        assert build.copr_message_id == msgobj.id

        # TODO We are waiting for JSON support in fedora-review to implement these
        assert build.status is None
        assert build.issues is None
