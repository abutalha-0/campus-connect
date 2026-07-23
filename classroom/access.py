"""
Access rules for a subject's content (resources & notices), shared across the
resources and notices apps.

Actors per subject:
  - Faculty who owns the subject.
  - The CR (creator) of a class that contains the subject.
  - Student members of such a class.
"""


def _user_class(user):
    """Return (classroom, is_creator) for the student's class, or (None, False)."""
    owned = getattr(user, 'owned_class', None)
    if owned is not None:
        return owned, True
    membership = getattr(user, 'class_membership', None)
    if membership is not None:
        return membership.classroom, False
    return None, False


def is_subject_faculty(user, subject):
    return getattr(user, 'role', None) == 'FACULTY' and subject.faculty.user_id == user.id


def can_view_subject(user, subject):
    """Faculty owner, or any student whose class contains the subject."""
    if is_subject_faculty(user, subject):
        return True
    classroom, _ = _user_class(user)
    return bool(classroom and classroom.subjects.filter(id=subject.id).exists())


def can_post_to_subject(user, subject):
    """Faculty owner, or the CR (class creator) whose class contains the subject."""
    if is_subject_faculty(user, subject):
        return True
    classroom, is_creator = _user_class(user)
    return bool(is_creator and classroom.subjects.filter(id=subject.id).exists())


def can_modify_content(user, subject, author_id):
    """The author of the item, or the subject's faculty owner (moderation)."""
    return author_id == user.id or is_subject_faculty(user, subject)
