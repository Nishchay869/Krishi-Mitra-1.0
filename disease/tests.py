from django.test import SimpleTestCase

from .treatments import advice_for, parse_class


class TreatmentTests(SimpleTestCase):
    def test_parses_plantvillage_class_names(self):
        self.assertEqual(parse_class('Tomato___Late_blight'), ('Tomato', 'late blight'))
        self.assertEqual(parse_class('Corn_(maize)___Common_rust_'), ('Corn (maize)', 'common rust'))

    def test_disease_gets_actionable_treatment(self):
        advice = advice_for('Potato___Early_blight')
        self.assertFalse(advice['is_healthy'])
        self.assertIn('mancozeb', advice['treatment'])

    def test_healthy_leaf(self):
        advice = advice_for('Apple___healthy')
        self.assertTrue(advice['is_healthy'])
        self.assertEqual(advice['disease'], 'Healthy')

    def test_unknown_disease_falls_back_to_kvk(self):
        self.assertIn('Krishi Vigyan Kendra', advice_for('Mango___Mystery_spot')['treatment'])
