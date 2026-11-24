import os
import unittest

from flask import Flask, render_template, session


class DashboardTemplateTests(unittest.TestCase):
    def test_progress_renders_and_is_capped_at_100_percent(self):
        template_folder = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'templates')
        )
        app = Flask(__name__, template_folder=template_folder)
        app.secret_key = 'test-secret'
        app.jinja_env.globals['url_for'] = (
            lambda endpoint, **values: f'/{endpoint}' + (f'?{values}' if values else '')
        )

        with app.test_request_context('/dashboard'):
            session['user_id'] = 1
            session['user_name'] = 'Test User'

            for total_notes, expected_progress in ((0, '0%'), (8, '100%')):
                with self.subTest(total_notes=total_notes):
                    html = render_template(
                        'dashboard.html',
                        user_name='Test User',
                        total_notes=total_notes,
                        notes=[],
                    )

                    self.assertIn(expected_progress, html)


if __name__ == '__main__':
    unittest.main()
