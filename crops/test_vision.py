import base64
import numpy as np
import cv2
from django.test import TestCase, Client
from django.urls import reverse

from advisory_matrix import ADVISORY_MATRIX, SeverityStage, TargetCategory, get_advisory
from vision_engine import PlantVisionEngine, DiagnosticResponse
from server import app as fastapi_app
from fastapi.testclient import TestClient


class PlantVisionAndIPMTests(TestCase):
    """Test suite for Real-Time Plant Vision & IPM Advisory System."""

    def setUp(self):
        self.engine = PlantVisionEngine()
        self.client = Client()
        self.fastapi_client = TestClient(fastapi_app)

    def test_advisory_matrix_stage_1_biological_priority(self):
        """Verify that Stage 1 strictly prescribes biological / botanical agents."""
        # 1. Early Blight Stage 1
        eb_stage1 = get_advisory("Early Blight", SeverityStage.STAGE_1)
        self.assertEqual(eb_stage1.severity_stage, SeverityStage.STAGE_1)
        self.assertIn("Bacillus subtilis", eb_stage1.active_agent)
        self.assertEqual(eb_stage1.phi_days, 0)
        self.assertIn("Biological Prophylactic", eb_stage1.strategy_type)

        # 2. Powdery Mildew Stage 1
        pm_stage1 = get_advisory("Powdery Mildew", SeverityStage.STAGE_1)
        self.assertIn("Potassium Bicarbonate", pm_stage1.active_agent)

        # 3. Aphids Stage 1
        aphid_stage1 = get_advisory("Aphids", SeverityStage.STAGE_1, is_pest=True)
        self.assertIn("Neem Oil", aphid_stage1.active_agent)
        self.assertEqual(aphid_stage1.category, TargetCategory.PEST)

    def test_advisory_matrix_escalation_to_stage_2_and_3(self):
        """Verify escalation to protective contact (Stage 2) and systemic chemistry (Stage 3)."""
        eb_stage2 = get_advisory("Early Blight", SeverityStage.STAGE_2)
        self.assertIn("Copper Oxychloride", eb_stage2.active_agent)
        self.assertEqual(eb_stage2.severity_stage, SeverityStage.STAGE_2)

        eb_stage3 = get_advisory("Early Blight", SeverityStage.STAGE_3)
        self.assertIn("Azoxystrobin", eb_stage3.active_agent)
        self.assertEqual(eb_stage3.severity_stage, SeverityStage.STAGE_3)
        self.assertGreaterEqual(eb_stage3.phi_days, 14)

    def test_laplacian_blur_and_motion_rejection(self):
        """Blur & Motion Rejection: Verify Laplacian variance rejects out-of-focus frames."""
        # Create an out-of-focus / uniform gray image (focus measure ~ 0.0 < 100.0)
        blurred_img = np.full((320, 320, 3), 128, dtype=np.uint8)
        diag = self.engine.analyze_frame(blurred_img)

        self.assertFalse(diag.success)
        self.assertTrue(diag.quality.is_blurred)
        self.assertFalse(diag.quality.is_acceptable)
        self.assertLess(diag.quality.focus_measure, 100.0)
        self.assertIn("out of focus or motion-blurred", diag.quality.status_message)

    def test_clahe_dynamic_lighting_calibration(self):
        """Dynamic Lighting Calibration: Verify CLAHE normalizes L-channel in LAB space."""
        img = np.random.randint(40, 180, (100, 100, 3), dtype=np.uint8)
        normalized, mean_l = self.engine.apply_clahe_normalization(img)

        self.assertEqual(normalized.shape, img.shape)
        self.assertIsInstance(mean_l, float)
        self.assertGreater(mean_l, 0)

    def test_digital_pathology_severity_mathematics(self):
        """Verify Surface Lesion Severity Index and Agronomic Staging mathematics."""
        h, w = 100, 100
        leaf_mask = np.full((h, w), 255, dtype=np.uint8)  # 10,000 leaf pixels
        lesion_mask = np.zeros((h, w), dtype=np.uint8)
        lesion_mask[:10, :20] = 255  # 200 lesion pixels -> (200 / 10000) * 100 = 2.0% (Stage 1)

        pest_mask = np.zeros((h, w), dtype=np.uint8)

        # 1. Stage 1 check (< 3% severity, low count)
        pathology_st1 = self.engine.calculate_pathology_metrics(
            leaf_mask=leaf_mask,
            lesion_mask=lesion_mask,
            pest_mask=pest_mask,
            lesion_count=2,
            pest_count=3,
            pixels_per_cm=40.0
        )
        self.assertEqual(pathology_st1.severity_index_pct, 2.0)
        self.assertEqual(pathology_st1.severity_stage, SeverityStage.STAGE_1)
        self.assertGreater(pathology_st1.calibrated_leaf_area_cm2, 0)

        # 2. Stage 2 check (3% - 15% severity)
        lesion_mask[:25, :32] = 255  # 800 lesion pixels -> 8.0%
        pathology_st2 = self.engine.calculate_pathology_metrics(
            leaf_mask=leaf_mask,
            lesion_mask=lesion_mask,
            pest_mask=pest_mask,
            lesion_count=6,
            pest_count=8,
            pixels_per_cm=40.0
        )
        self.assertEqual(pathology_st2.severity_index_pct, 8.0)
        self.assertEqual(pathology_st2.severity_stage, SeverityStage.STAGE_2)

        # 3. Stage 3 check (> 15% severity)
        lesion_mask[:50, :40] = 255  # 2,000 lesion pixels -> 20.0%
        pathology_st3 = self.engine.calculate_pathology_metrics(
            leaf_mask=leaf_mask,
            lesion_mask=lesion_mask,
            pest_mask=pest_mask,
            lesion_count=20,
            pest_count=15,
            pixels_per_cm=40.0
        )
        self.assertEqual(pathology_st3.severity_index_pct, 20.0)
        self.assertEqual(pathology_st3.severity_stage, SeverityStage.STAGE_3)

    def test_django_vision_api_endpoint(self):
        """Test Django /crops/api/crop-vision/diagnose/ endpoint."""
        # Create sharp test leaf
        img = np.zeros((300, 300, 3), dtype=np.uint8)
        cv2.ellipse(img, (150, 150), (100, 60), 0, 0, 360, (30, 150, 40), -1)
        noise = np.random.randint(0, 30, img.shape, dtype=np.uint8)
        img = cv2.add(img, noise)
        _, buf = cv2.imencode('.jpg', img)
        b64_str = 'data:image/jpeg;base64,' + base64.b64encode(buf).decode('utf-8')

        url = reverse('crops:crop_vision_diagnose')
        response = self.client.post(
            url,
            data={'frame': b64_str, 'target_hint': 'Powdery Mildew'},
            HTTP_HOST='127.0.0.1'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('quality', data)
        self.assertIn('polygons', data)
        self.assertIn('prescription', data)

    def test_fastapi_server_diagnose(self):
        """Test FastAPI server.py endpoints."""
        health = self.fastapi_client.get('/health')
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()['status'], 'healthy')

        # Create synthetic sharp leaf
        img = np.zeros((200, 200, 3), dtype=np.uint8)
        cv2.ellipse(img, (100, 100), (80, 50), 0, 0, 360, (25, 140, 35), -1)
        noise = np.random.randint(0, 30, img.shape, dtype=np.uint8)
        img = cv2.add(img, noise)
        _, buf = cv2.imencode('.jpg', img)
        b64_str = 'data:image/jpeg;base64,' + base64.b64encode(buf).decode('utf-8')

        res = self.fastapi_client.post(
            '/api/crop-vision/diagnose',
            json={'frame': b64_str, 'target_hint': 'Rust'}
        )
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertTrue(body['success'])
        self.assertIsNotNone(body['prescription'])

    def test_root_crop_vision_diagnose_endpoint(self):
        """Test root /api/crop-vision/diagnose/ endpoint."""
        img = np.zeros((200, 200, 3), dtype=np.uint8)
        cv2.ellipse(img, (100, 100), (80, 50), 0, 0, 360, (25, 140, 35), -1)
        noise = np.random.randint(0, 30, img.shape, dtype=np.uint8)
        img = cv2.add(img, noise)
        _, buf = cv2.imencode('.jpg', img)
        b64_str = 'data:image/jpeg;base64,' + base64.b64encode(buf).decode('utf-8')

        response = self.client.post(
            '/api/crop-vision/diagnose/',
            data={'frame': b64_str, 'target_hint': 'Early Blight'},
            HTTP_HOST='127.0.0.1'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('polygons', data)

    def test_distinct_prescriptions_per_disease(self):
        """Verify each disease species receives its exact, unique medicine prescription."""
        disease_expectations = {
            'Early Blight': 'Azoxystrobin',
            'Powdery Mildew': 'Tebuconazole',
            'Rust': 'Pyraclostrobin',
            'Downy Mildew': 'Dimethomorph',
            'Anthracnose': 'Trifloxystrobin',
            'Late Blight': 'Metalaxyl',
            'Bacterial Spot': 'Kasugamycin',
            'Aphids': 'Spirotetramat',
            'Spider Mites': 'Abamectin',
            'Thrips': 'Spinetoram',
            'Whiteflies': 'Diafenthiuron',
        }

        # Create base test leaf
        img = np.zeros((200, 200, 3), dtype=np.uint8)
        cv2.ellipse(img, (100, 100), (80, 50), 0, 0, 360, (25, 140, 35), -1)
        noise = np.random.randint(0, 30, img.shape, dtype=np.uint8)
        img = cv2.add(img, noise)
        _, buf = cv2.imencode('.jpg', img)
        b64_str = 'data:image/jpeg;base64,' + base64.b64encode(buf).decode('utf-8')

        seen_agents = set()
        for disease, expected_agent in disease_expectations.items():
            diag = self.engine.analyze_frame(b64_str, target_hint=disease)
            self.assertTrue(diag.success)
            self.assertIsNotNone(diag.prescription)
            self.assertEqual(diag.diagnosed_target, disease)
            self.assertIn(expected_agent.lower(), diag.stage_prescriptions['stage_3'].active_agent.lower())
            self.assertIsNotNone(diag.stage_prescriptions)
            self.assertIn('stage_1', diag.stage_prescriptions)
            self.assertIn('stage_2', diag.stage_prescriptions)
            self.assertIn('stage_3', diag.stage_prescriptions)
            seen_agents.add(diag.prescription.active_agent)

        # Confirm all 11 diseases have distinct active chemical agents
        self.assertEqual(len(seen_agents), len(disease_expectations))

    def test_healthy_leaf_recognition(self):
        """Verify healthy leaves are accurately identified with 0.0% severity and prophylactic advice."""
        # 1. Test with real healthy leaf photo
        healthy_path = 'static/images/pests/healthy-tomato.jpg'
        diag = self.engine.analyze_frame(healthy_path, target_hint='Auto')
        self.assertTrue(diag.success)
        self.assertEqual(diag.diagnosed_target, 'Healthy')
        self.assertEqual(diag.pathology.severity_index_pct, 0.0)
        self.assertEqual(diag.pathology.lesion_count, 0)
        self.assertEqual(diag.pathology.pest_count, 0)
        self.assertIn('seaweed', diag.prescription.active_agent.lower())
        self.assertIn('optimal chlorophyll', diag.alert_banner.lower())
        # Ensure only leaf polygon is returned (no false lesion or pest marks)
        polygon_classes = {p.class_name for p in diag.polygons}
        self.assertTrue(polygon_classes.issubset({'leaf'}))

        # 2. Test with explicit 'Healthy' target hint
        diag_hint = self.engine.analyze_frame(healthy_path, target_hint='Healthy')
        self.assertTrue(diag_hint.success)
        self.assertEqual(diag_hint.diagnosed_target, 'Healthy')
        self.assertEqual(diag_hint.pathology.severity_index_pct, 0.0)
        self.assertIn('seaweed', diag_hint.prescription.active_agent.lower())

