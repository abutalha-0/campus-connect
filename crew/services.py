from django.utils import timezone

from .models import JoinRequest, PostMember


def accept_join_request(join_request, reviewer):
    """Accept a JoinRequest: creates the PostMember, marks the request
    accepted, and auto-closes the post if it just reached capacity.
    Returns the updated JoinRequest.
    """
    post = join_request.post

    join_request.status = 'ACCEPTED'
    join_request.reviewed_by = reviewer
    join_request.reviewed_at = timezone.now()
    join_request.save(update_fields=['status', 'reviewed_by', 'reviewed_at'])

    PostMember.objects.get_or_create(post=post, user=join_request.requester)

    if post.is_full and post.status == 'OPEN':
        post.status = 'FULL'
        post.save(update_fields=['status'])

    return join_request


def reject_join_request(join_request, reviewer):
    join_request.status = 'REJECTED'
    join_request.reviewed_by = reviewer
    join_request.reviewed_at = timezone.now()
    join_request.save(update_fields=['status', 'reviewed_by', 'reviewed_at'])
    return join_request


def close_post(post):
    post.status = 'CLOSED'
    post.save(update_fields=['status'])
    return post


def cancel_stale_pending_requests(post):
    """Called when a post is closed/full: cancels any requests still
    pending so they stop showing as actionable to either side.
    """
    JoinRequest.objects.filter(post=post, status='PENDING').update(status='CANCELLED')
