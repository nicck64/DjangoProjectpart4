import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


# Helper function → CLASS-ların xaricində olmalıdır!
def create_question(question_text, days):
    """
    Create a question with the given `question_text` and publish it the
    given number of `days` offset to now (negative for past questions,
    positive for future questions).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() future tarix üçün False qaytarmalıdır.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        question = Question(pub_date=time)
        self.assertIs(question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() → 1 gündən çox köhnə sual üçün False.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        question = Question(pub_date=time)
        self.assertIs(question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() → son 1 gün içindədirsə True.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        question = Question(pub_date=time)
        self.assertIs(question.was_published_recently(), True)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        Heç sual yoxdursa uyğun mesaj göstərilməlidir.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Keçmişdəki suallar indexdə görünməlidir.
        """
        question = create_question("Past question.", -30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question])

    def test_future_question(self):
        """
        Gələcək tarixli suallar indexdə görünməməlidir.
        """
        create_question("Future question.", 30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Keçmiş + gələcək birlikdə olsa belə → yalnız keçmiş görünməlidir.
        """
        past_q = create_question("Past question.", -30)
        create_question("Future question.", 30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [past_q])

    def test_two_past_questions(self):
        """
        Index səhifəsi birdən çox keçmiş sualı düz sırada göstərməlidir.
        """
        q1 = create_question("Past question 1.", -30)
        q2 = create_question("Past question 2.", -5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [q2, q1]
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        Gələcək tarixli sual → detail səhifəsində 404 verməlidir.
        """
        future_question = create_question("Future question.", 5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        Keçmiş sual → detail səhifəsində mətn görünməlidir.
        """
        past_question = create_question("Past question.", -5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
