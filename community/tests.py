from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import CommunityPost, CommunityAnswer
from .seed_data import ensure_community_seed_data

User = get_user_model()


class CommunityTests(TestCase):
    def setUp(self):
        self.client = Client()
        ensure_community_seed_data()
        self.post = CommunityPost.objects.first()

    def test_feed_view_loads_successfully(self):
        response = self.client.get(reverse('community:feed'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'community/feed.html')
        self.assertContains(response, 'Search in Community')
        self.assertContains(response, 'Filter by')
        self.assertContains(response, 'Ask Community')
        self.assertGreaterEqual(len(response.context['posts']), 1)

    def test_feed_filter_by_crop(self):
        response = self.client.get(reverse('community:feed') + '?crop=Tomato')
        self.assertEqual(response.status_code, 200)
        for post in response.context['posts']:
            self.assertIn('Tomato', post.crop)

    def test_feed_search_query(self):
        response = self.client.get(reverse('community:feed') + '?q=Chilli')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any('Chilli' in p.title or 'Chilli' in p.description for p in response.context['posts']))

    def test_ask_community_get(self):
        response = self.client.get(reverse('community:ask'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'community/ask.html')
        self.assertContains(response, 'Your question to the community')
        self.assertContains(response, 'Description of your problem')

    def test_ask_community_post_creates_problem(self):
        data = {
            'title': 'Leaves curling inwards with white spots',
            'description': 'Lower leaves of my cotton plants show inward curling and pale spots.',
            'crop': 'Cotton',
            'author_name': 'Ramesh Kumar'
        }
        response = self.client.post(reverse('community:ask'), data=data)
        self.assertRedirects(response, reverse('community:feed'))

        new_post = CommunityPost.objects.filter(title='Leaves curling inwards with white spots').first()
        self.assertIsNotNone(new_post)
        self.assertEqual(new_post.crop, 'Cotton')
        self.assertEqual(new_post.author_name, 'Ramesh Kumar')

    def test_post_detail_view(self):
        response = self.client.get(reverse('community:detail', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'community/detail.html')
        self.assertContains(response, self.post.title)

    def test_post_vote_toggle(self):
        url = reverse('community:vote', args=[self.post.id])
        initial_likes = self.post.likes

        # Like post
        res = self.client.post(url, data={'action': 'like'})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['likes'], initial_likes + 1)
        self.assertEqual(data['current_vote'], 'like')

        # Toggle like off
        res2 = self.client.post(url, data={'action': 'like'})
        data2 = res2.json()
        self.assertEqual(data2['likes'], initial_likes)
        self.assertIsNone(data2['current_vote'])

    def test_post_answer_submission(self):
        url = reverse('community:answer', args=[self.post.id])
        initial_answers = self.post.answers.count()

        res = self.client.post(
            url,
            data={'content': 'Spray Mancozeb 75 WP @ 2g/L on foliage.', 'author_name': 'Suresh Agronomist'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['answers_count'], initial_answers + 1)
        self.assertEqual(data['answer']['author_name'], 'Suresh Agronomist')

    def test_lower_navbar_has_community_link(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/community/"')

    def test_reply_triggers_notification_for_post_author(self):
        from .models import CommunityNotification
        # Create a post with a known session
        author_client = Client()
        author_session = author_client.session
        author_session['init'] = True
        author_session.save()
        author_session_key = author_session.session_key

        post = CommunityPost.objects.create(
            title="Yellow spots on okra leaves",
            description="Okra leaves showing yellow patches along veins.",
            crop="Okra",
            author_name="Ravi Farmer",
            author_session_key=author_session_key
        )

        # Another user submits an answer
        reply_client = Client()
        url = reverse('community:answer', args=[post.id])
        res = reply_client.post(
            url,
            data={'content': 'This looks like Yellow Vein Mosaic Virus. Apply Neem oil spray.', 'author_name': 'Dr. Kulkarni'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['success'])

        # Check notification was created for Ravi Farmer
        notif = CommunityNotification.objects.filter(post=post, recipient_session_key=author_session_key).first()
        self.assertIsNotNone(notif)
        self.assertIn('Dr. Kulkarni', notif.message)
        self.assertIn('Yellow Vein Mosaic Virus', notif.message)
        self.assertFalse(notif.is_read)

    def test_answer_vote_helpful(self):
        answer = CommunityAnswer.objects.create(
            post=self.post,
            content="Use neem oil spray for initial defense.",
            author_name="Ramesh",
            author_role="Agronomist"
        )
        initial_likes = answer.likes

        url = reverse('community:answer_vote', args=[answer.id])
        res = self.client.post(url, data={'action': 'like'})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['likes'], initial_likes + 1)
        self.assertEqual(data['current_vote'], 'like')

        # Toggle off
        res2 = self.client.post(url, data={'action': 'like'})
        self.assertEqual(res2.json()['likes'], initial_likes)
        self.assertIsNone(res2.json()['current_vote'])

    def test_exact_published_time_rendered(self):
        response = self.client.get(reverse('community:feed'))
        self.assertEqual(response.status_code, 200)
        # Check that post-exact-time class with clock icon exists
        self.assertContains(response, 'post-exact-time')
        self.assertContains(response, 'bi-clock')
        self.assertContains(response, 'ago')

    def test_translate_api_endpoint(self):
        url = reverse('community:translate', args=[self.post.id]) + '?lang=hi'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('title', data)
        self.assertIn('description', data)
        self.assertIn('Hindi', data['target_lang'])

    def test_notifications_api_and_mark_read(self):
        # Fetch notifications endpoint
        res = self.client.get(reverse('community:notifications_api'))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertIn('notifications', data)

        # Mark all read endpoint
        mark_res = self.client.post(reverse('community:notifications_read'))
        self.assertEqual(mark_res.status_code, 200)
        self.assertEqual(mark_res.json()['unread_count'], 0)

    def test_admin_portal_community_models_registered(self):
        from django.contrib import admin
        from .models import CommunityPost, CommunityAnswer, CommunityNotification
        self.assertIn(CommunityPost, admin.site._registry)
        self.assertIn(CommunityAnswer, admin.site._registry)
        self.assertIn(CommunityNotification, admin.site._registry)

