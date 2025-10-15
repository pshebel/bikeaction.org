from celery import shared_task
from django.conf import settings
from django.urls import reverse

from elections.models import Nomination, get_user_display_name
from pbaabp.email import send_email_message


@shared_task
def send_nomination_notification(nomination_id):
    """Send email notification to nominee for a specific nomination."""

    try:
        nomination = Nomination.objects.select_related(
            "nominee__user", "nominee__election", "nominator"
        ).get(id=nomination_id)
    except Nomination.DoesNotExist:
        return f"Nomination {nomination_id} not found"

    user = nomination.nominee.user
    election = nomination.nominee.election
    nominator = nomination.nominator

    # Build the respond URL
    respond_path = reverse(
        "nomination_respond",
        kwargs={"election_slug": election.slug, "pk": nomination.id},
    )
    respond_url = f"{settings.SITE_URL}{respond_path}"

    # Prepare email message
    message = f"""
You have been nominated for **{election.title}**!

**Nominated by:** {get_user_display_name(nominator)}

Please respond to this nomination by visiting:

[Respond to Nomination]({respond_url})

You can accept or decline this nomination. If you accept, please make sure to complete
your nominee profile with a photo and acknowledgment of board responsibilities.

**Important Dates:**

- Nominations close: {election.nominations_close.strftime("%B %d, %Y at %I:%M %p")}
- Voting opens: {election.voting_opens.strftime("%B %d, %Y")}

---

**Nomination Statement:**

{nomination.nomination_statement}

---

Thank you for your participation!
"""

    # Send email using the standard utility
    send_email_message(
        template_name=None,
        from_=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
        context={},
        subject=f"You've been nominated for {election.title}",
        message=message,
    )

    return f"Sent nomination notification to {user.email} for {election.title}"
