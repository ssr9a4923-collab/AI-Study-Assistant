import os
import sqlite3
import tempfile
import unittest
from unittest.mock import Mock, patch

from core_classes import (
    AIClient,
    AppLogic,
    DatabaseManager,
    chunk_document_pages,
    retrieve_relevant_chunks,
)


class RegistrationTests(unittest.TestCase):
    def test_database_path_environment_variable_creates_parent_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, 'persistent', 'study.db')
            with patch.dict(os.environ, {'DATABASE_PATH': db_path}):
                db = DatabaseManager()

            self.assertEqual(db.db_path, os.path.abspath(db_path))
            self.assertTrue(os.path.isfile(db.db_path))

    def test_duplicate_email_is_reported_as_duplicate(self):
        logic = AppLogic.__new__(AppLogic)
        logic.db = Mock()
        logic.db.create_user.return_value = False

        result = logic.register_user('Test User', 'taken@example.test', 'password')

        self.assertFalse(result['success'])
        self.assertIn('already exists', result['message'])

    def test_database_errors_are_not_reported_as_duplicate_emails(self):
        logic = AppLogic.__new__(AppLogic)
        logic.db = Mock()
        logic.db.create_user.side_effect = sqlite3.OperationalError('database is locked')

        with self.assertRaisesRegex(sqlite3.OperationalError, 'database is locked'):
            logic.register_user('Test User', 'new@example.test', 'password')


class AIClientTests(unittest.TestCase):
    def test_note_prompt_uses_groq_responses_api(self):
        with patch.dict(os.environ, {'GROQ_API_KEY': 'test-key'}):
            with patch('core_classes.OpenAI') as openai:
                openai.return_value.responses.create.return_value.output_text = 'Summary'
                client = AIClient()

                self.assertEqual(client.generate_summary('Study content'), 'Summary')

        openai.assert_called_once_with(
            api_key='test-key',
            base_url='https://api.groq.com/openai/v1',
        )
        request = openai.return_value.responses.create.call_args.kwargs
        self.assertEqual(request['model'], 'openai/gpt-oss-20b')
        self.assertIn('Study content', request['input'])

    def test_pdf_answer_uses_groq_responses_api(self):
        with patch.dict(os.environ, {'GROQ_API_KEY': 'test-key'}):
            with patch('core_classes.OpenAI') as openai:
                openai.return_value.responses.create.return_value.output_text = 'Answer'
                client = AIClient()
                answer = client.answer_from_sources(
                    'What is photosynthesis?',
                    [{
                        'filename': 'Biology.pdf',
                        'page_number': 4,
                        'content': 'Photosynthesis occurs in chloroplasts.',
                    }],
                )

        self.assertEqual(answer, 'Answer')
        request = openai.return_value.responses.create.call_args.kwargs
        self.assertEqual(request['model'], 'openai/gpt-oss-20b')
        self.assertIn('What is photosynthesis?', request['input'])
        self.assertIn('Biology.pdf, page 4', request['input'])

    def test_pdf_answer_requires_groq_api_key(self):
        with patch.dict(os.environ, {'GROQ_API_KEY': ''}):
            client = AIClient()

        with self.assertRaisesRegex(RuntimeError, 'GROQ_API_KEY'):
            client.answer_from_sources('Question', [])


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.chunks = [
            {
                'filename': 'Biology.pdf',
                'page_number': 4,
                'content': (
                    'Photosynthesis takes place in chloroplasts. Chlorophyll absorbs '
                    'light energy, which helps convert carbon dioxide and water into '
                    'glucose and oxygen.'
                )
            },
            {
                'filename': 'History.pdf',
                'page_number': 2,
                'content': 'The industrial revolution began in Britain in the 18th century.'
            },
        ]

    def test_retrieves_relevant_passage_with_page_metadata(self):
        matches = retrieve_relevant_chunks(
            'Where does photosynthesis take place?', self.chunks
        )

        self.assertTrue(matches)
        self.assertEqual(matches[0]['filename'], 'Biology.pdf')
        self.assertEqual(matches[0]['page_number'], 4)

    def test_returns_no_passages_for_unrelated_question(self):
        matches = retrieve_relevant_chunks(
            'Who won the world cup?', self.chunks
        )

        self.assertEqual(matches, [])

    def test_chunking_keeps_page_numbers_and_overlaps(self):
        text = ' '.join(f'word{index}' for index in range(500))
        chunks = chunk_document_pages(
            [{'page_number': 7, 'content': text}],
            chunk_size=300,
            overlap=40
        )

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(chunk['page_number'] == 7 for chunk in chunks))
        self.assertTrue(set(chunks[0]['content'].split()[-5:]) &
                        set(chunks[1]['content'].split()[:10]))


class DocumentOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = DatabaseManager(os.path.join(self.temp_dir.name, 'test.db'))
        self.db.create_user('First user', 'first@example.test', 'password')
        self.db.create_user('Second user', 'second@example.test', 'password')
        self.first_user_id = self.db.authenticate_user(
            'first@example.test', 'password'
        )['id']
        self.second_user_id = self.db.authenticate_user(
            'second@example.test', 'password'
        )['id']
        self.document_id = self.db.add_document(
            self.first_user_id,
            'Biology.pdf',
            1,
            [{'page_number': 1, 'content': 'Photosynthesis uses light energy.'}]
        )

    def tearDown(self):
        self.db = None
        self.temp_dir.cleanup()

    def test_document_chunks_are_scoped_to_the_owner(self):
        self.assertEqual(len(self.db.get_user_document_chunks(self.first_user_id)), 1)
        self.assertEqual(self.db.get_user_document_chunks(self.second_user_id), [])

    def test_another_user_cannot_delete_document(self):
        self.assertFalse(
            self.db.delete_user_document(self.document_id, self.second_user_id)
        )
        self.assertEqual(len(self.db.get_user_documents(self.first_user_id)), 1)


if __name__ == '__main__':
    unittest.main()
