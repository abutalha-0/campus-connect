import random
from datetime import date, time, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from users.accounts.models import User
from users.student_profile.models import Profile, Education, Experience, Project, Skill, UserSkill, Link
from users.faculty_profile.models import FacultyProfile, FacultyLink
from classroom.subjects.models import Subject
from classroom.resources.models import Resource
from classroom.notices.models import Notice
from classroom.classes.models import Classroom, ClassMembership
from classroom.feed.models import FeedPost, FeedVote, FeedComment

EMAIL_DOMAIN = 'bubt.demo'
PASSWORD = 'Campus@123'

# (full_name, department, designation, employee_id, is_verified, [
#     (subject_name, intake, section, room), ...
# ])
FACULTY = [
    ('Dr. Farhana Islam', 'Computer Science & Engineering', 'ASSOCIATE_PROFESSOR', 'BUBT-CSE-101', True, [
        ('Data Structures and Algorithms', '45', 'B', '402'),
        ('Database Management Systems', '44', 'A', '301'),
    ]),
    ('Prof. Kamal Uddin', 'Computer Science & Engineering', 'PROFESSOR', 'BUBT-CSE-102', True, [
        ('Operating Systems', '44', 'A', '305'),
        ('Software Engineering', '45', 'B', '402'),
    ]),
    ('Dr. Shirin Akter', 'Computer Science & Engineering', 'ASSISTANT_PROFESSOR', 'BUBT-CSE-103', True, [
        ('Computer Networks', '44', 'B', '210'),
        ('Artificial Intelligence', '45', 'A', '301'),
    ]),
    ('Prof. Rezaul Karim', 'Electrical & Electronic Engineering', 'PROFESSOR', 'BUBT-EEE-104', True, [
        ('Digital Electronics', '44', 'A', '108'),
        ('Signals and Systems', '45', 'B', '108'),
    ]),
    ('Dr. Nabila Hasan', 'Business Administration', 'ASSOCIATE_PROFESSOR', 'BUBT-BBA-105', False, [
        ('Principles of Management', '44', 'A', '501'),
        ('Business Communication', '45', 'B', '502'),
    ]),
]

# (full_name, gender, user_type)
STUDENTS = [
    ('Bilal Ahmed', 'Male', 'CR'),
    ('Sara Khan', 'Female', 'CR'),
    ('Ayesha Noor', 'Female', 'STUDENT'),
    ('Imran Raza', 'Male', 'STUDENT'),
    ('Md. Rakibul Islam', 'Male', 'STUDENT'),
    ('Sabbir Ahmed', 'Male', 'STUDENT'),
    ('Tania Akter', 'Female', 'STUDENT'),
    ('Nusrat Jahan', 'Female', 'STUDENT'),
    ('Arafat Hossain', 'Male', 'STUDENT'),
    ('Farhana Yasmin', 'Female', 'STUDENT'),
    ('Kamrul Hasan', 'Male', 'STUDENT'),
    ('Sadia Islam', 'Female', 'STUDENT'),
    ('Tanvir Ahmed', 'Male', 'STUDENT'),
    ('Mehjabin Chowdhury', 'Female', 'STUDENT'),
    ('Ayesha Siddika', 'Female', 'STUDENT'),
    ('Shakil Ahmed', 'Male', 'STUDENT'),
    ('Jannatul Ferdous', 'Female', 'STUDENT'),
    ('Mahmudul Hasan', 'Male', 'STUDENT'),
    ('Shamima Nasrin', 'Female', 'STUDENT'),
    ('Asif Mahmud', 'Male', 'STUDENT'),
]

SKILL_POOL = [
    'Python', 'Java', 'C++', 'JavaScript', 'Django', 'React Native', 'Flutter',
    'MySQL', 'Git', 'Figma', 'Machine Learning', 'Data Structures',
    'Android (Java)', 'Node.js', 'HTML & CSS',
]

BIOS = [
    "CSE undergrad at BUBT, into competitive programming.",
    "Trying to survive midterms one cup of cha at a time.",
    "Backend curious, frontend cautious.",
    "Football on weekends, code on weekdays.",
    "Debugging life one semester at a time.",
    "Aspiring software engineer from Dhaka.",
    "Loves a good hackathon and biryani.",
]


class Command(BaseCommand):
    help = "Seed the database with demo BUBT students and faculty (idempotent — safe to re-run)."

    def handle(self, *args, **options):
        random.seed(42)
        with transaction.atomic():
            self._clear_previous()
            faculty_profiles = self._create_faculty()
            students = self._create_students()
            subjects_by_faculty = self._create_subjects(faculty_profiles)
            class_a, class_b = self._create_classes(students, subjects_by_faculty)
            self._create_resources(subjects_by_faculty)
            self._create_notices(subjects_by_faculty, students)
            self._create_feed(class_a, class_b)

        self._print_summary(faculty_profiles, students)

    def _clear_previous(self):
        deleted, _ = User.objects.filter(email__iendswith=f'@{EMAIL_DOMAIN}').delete()
        if deleted:
            self.stdout.write(f"Cleared {deleted} previously seeded record(s).")

    # ---- users ----------------------------------------------------------

    def _create_faculty(self):
        profiles = []
        for i, (full_name, department, designation, employee_id, is_verified, _subjects) in enumerate(FACULTY, start=1):
            email = f'faculty{i:02d}@{EMAIL_DOMAIN}'
            user = User.objects.create_user(
                email=email,
                username=f'faculty{i:02d}',
                full_name=full_name,
                password=PASSWORD,
                role='FACULTY',
            )
            fp = FacultyProfile.objects.create(
                user=user,
                employee_id=employee_id,
                department=department,
                designation=designation,
                is_verified=is_verified,
            )
            if i % 2 == 0:
                FacultyLink.objects.create(faculty=fp, link_name='LinkedIn', icon='linkedin',
                                            url=f'https://linkedin.com/in/{user.username}')
            profiles.append(fp)
        return profiles

    def _create_students(self):
        users = []
        for i, (full_name, gender, user_type) in enumerate(STUDENTS, start=1):
            email = f'student{i:02d}@{EMAIL_DOMAIN}'
            user = User.objects.create_user(
                email=email,
                username=f'student{i:02d}',
                full_name=full_name,
                password=PASSWORD,
                role='STUDENT',
                bio=random.choice(BIOS),
            )
            # Signal already created a bare Profile; fill it in.
            profile = user.student_profile
            profile.bio = random.choice(BIOS)
            profile.about = f"{full_name.split()[0]} is a Computer Science & Engineering student at BUBT."
            profile.dob = date(random.randint(2001, 2005), random.randint(1, 12), random.randint(1, 28))
            profile.gender = gender
            profile.user_type = user_type
            profile.save()

            Education.objects.create(
                user=user,
                institution_name='Bangladesh University of Business and Technology (BUBT)',
                degree='B.Sc. in Computer Science & Engineering',
                start_year=random.choice([2022, 2023, 2024]),
                end_year=None,
            )

            for skill_name in random.sample(SKILL_POOL, k=random.randint(2, 4)):
                skill, _ = Skill.objects.get_or_create(name=skill_name, defaults={'is_predefined': True})
                UserSkill.objects.get_or_create(
                    user=user, skill=skill,
                    defaults={'proficiency': random.choice(['BEGINNER', 'INTERMEDIATE', 'ADVANCED'])},
                )

            if i % 3 == 0:
                Link.objects.create(user=user, link_name='GitHub', icon='github',
                                     url=f'https://github.com/{user.username}')

            if i % 4 == 0:
                Project.objects.create(
                    user=user,
                    name='Campus Connect Clone',
                    description='A course project replicating a classroom app for BUBT students.',
                    associated_with='BUBT CSE Coursework',
                )

            if i % 5 == 0:
                Experience.objects.create(
                    user=user,
                    title='Intern, Software Development',
                    organization='Brain Station 23',
                    description='Worked on internal tooling during summer break.',
                    start_date=date.today() - timedelta(days=180),
                    end_date=date.today() - timedelta(days=90),
                )

            users.append(user)
        return users

    # ---- subjects ---------------------------------------------------------

    def _create_subjects(self, faculty_profiles):
        subjects_by_faculty = {}
        for fp, (_, _, _, _, _, subject_defs) in zip(faculty_profiles, FACULTY):
            created = []
            for name, intake, section, room in subject_defs:
                subject = Subject.objects.create(
                    faculty=fp,
                    name=name,
                    intake=intake,
                    section=section,
                    room=room,
                    code=Subject.generate_unique_code(),
                )
                created.append(subject)
            subjects_by_faculty[fp.employee_id] = created
        return subjects_by_faculty

    # ---- classes ------------------------------------------------------

    def _create_classes(self, students, subjects_by_faculty):
        by_name = {}
        for subjects in subjects_by_faculty.values():
            for s in subjects:
                by_name[s.name] = s

        bilal = next(u for u in students if u.username == 'student01')
        sara = next(u for u in students if u.username == 'student02')

        class_a = Classroom.objects.create(creator=bilal, code=Classroom.generate_unique_code())
        class_a.subjects.set([
            by_name['Data Structures and Algorithms'],
            by_name['Software Engineering'],
            by_name['Artificial Intelligence'],
            by_name['Signals and Systems'],
            by_name['Business Communication'],
        ])

        class_b = Classroom.objects.create(creator=sara, code=Classroom.generate_unique_code())
        class_b.subjects.set([
            by_name['Database Management Systems'],
            by_name['Operating Systems'],
            by_name['Computer Networks'],
            by_name['Digital Electronics'],
            by_name['Principles of Management'],
        ])

        class_a_usernames = {f'student{n:02d}' for n in [3, 4, 5, 6, 7, 8, 9, 10, 11]}
        class_b_usernames = {f'student{n:02d}' for n in [12, 13, 14, 15, 16, 17, 18]}

        for u in students:
            if u.username in class_a_usernames:
                ClassMembership.objects.create(classroom=class_a, student=u)
            elif u.username in class_b_usernames:
                ClassMembership.objects.create(classroom=class_b, student=u)

        return class_a, class_b

    # ---- resources ------------------------------------------------------

    def _create_resources(self, subjects_by_faculty):
        by_name = {s.name: (s, s.faculty) for subs in subjects_by_faculty.values() for s in subs}

        entries = [
            ('Data Structures and Algorithms', 'Course Syllabus - Intake 45', 'PDF', 'Full trimester coverage plan.'),
            ('Data Structures and Algorithms', 'Lecture 1 Slides - Arrays & Linked Lists', 'PPT', ''),
            ('Data Structures and Algorithms', 'Sorting Algorithms Cheat Sheet', 'DOC', ''),
            ('Database Management Systems', 'ER Diagram Practice Sheet', 'PDF', ''),
            ('Database Management Systems', 'SQL Lab Manual', 'DOC', 'Covers joins, subqueries and normalization.'),
            ('Operating Systems', 'Process Scheduling Notes', 'PDF', ''),
            ('Artificial Intelligence', 'Search Algorithms Slides', 'PPT', ''),
        ]
        for subject_name, title, rtype, desc in entries:
            subject, fp = by_name[subject_name]
            Resource.objects.create(
                subject=subject, author=fp.user, title=title,
                resource_type=rtype, description=desc,
            )

    # ---- notices --------------------------------------------------------

    def _create_notices(self, subjects_by_faculty, students):
        by_name = {s.name: (s, s.faculty) for subs in subjects_by_faculty.values() for s in subs}
        today = timezone.localdate()
        bilal = next(u for u in students if u.username == 'student01')
        sara = next(u for u in students if u.username == 'student02')

        faculty_notices = [
            ('Data Structures and Algorithms', 'Midterm Exam Schedule', 'Midterm',
             'Midterm will cover arrays, linked lists and stacks/queues.', today + timedelta(days=6), time(10, 0)),
            ('Data Structures and Algorithms', 'Assignment 2 Deadline', 'Deadline',
             'Submit your sorting algorithm implementation via the classroom portal.', today + timedelta(days=3), time(23, 59)),
            ('Database Management Systems', 'Class Rescheduled to Room 301', '',
             'Tomorrow\'s class has been moved from Room 305 to Room 301.', today + timedelta(days=1), time(9, 0)),
            ('Software Engineering', 'Project Proposal Submission', 'Submission',
             'Submit your group project proposal before the deadline.', today + timedelta(days=9), time(17, 0)),
            ('Artificial Intelligence', 'Quiz 1 on Search Algorithms', 'Quiz',
             'Covers BFS, DFS and A* search.', today + timedelta(days=4), time(11, 0)),
            ('Computer Networks', 'Lab Class Cancelled Tomorrow', '',
             'Lab class is cancelled due to a faculty meeting. Will be rescheduled.', today + timedelta(days=1), None),
        ]
        for subject_name, title, highlight, text, event_date, event_time in faculty_notices:
            subject, fp = by_name[subject_name]
            Notice.objects.create(
                subject=subject, author=fp.user, title=title, text=text,
                highlight=highlight, event_date=event_date, event_time=event_time,
            )

        cr_notices = [
            (bilal, 'Artificial Intelligence', 'Reminder: Bring Laptops for AI Lab',
             'Everyone please bring your laptops charged for tomorrow\'s AI lab session.', today + timedelta(days=1)),
            (sara, 'Operating Systems', 'Study Group This Friday',
             'Organizing a study group before the midterm. Meet at the library, 2nd floor.', today + timedelta(days=2)),
        ]
        for cr_user, subject_name, title, text, event_date in cr_notices:
            subject, _ = by_name[subject_name]
            Notice.objects.create(
                subject=subject, author=cr_user, title=title, text=text,
                highlight='', event_date=event_date, event_time=time(18, 0),
            )

    # ---- feed -------------------------------------------------------------

    def _create_feed(self, class_a, class_b):
        a_members = [m.student for m in class_a.memberships.all()] + [class_a.creator]
        b_members = [m.student for m in class_b.memberships.all()] + [class_b.creator]

        posts_a = [
            (class_a.creator, 'Data Structures and Algorithms',
             'Anyone up for a DSA study session?', 'Thinking of meeting at the library this weekend before the midterm. Reply if interested.'),
            (a_members[1], 'Dr. Farhana Islam',
             'Assignment 2 clarification', 'Does the sorting assignment need both merge sort and quick sort, or just one?'),
            (a_members[2], '',
             'Load shedding during class', 'Power went out during today\'s lecture, did anyone record the last 15 minutes?'),
        ]
        posts_b = [
            (class_b.creator, 'Operating Systems',
             'Process scheduling numericals', 'Sharing my solved numericals for the scheduling algorithms, let me know if anything looks off.'),
            (b_members[1], '',
             'Rickshaw strike near campus', 'Heads up, there\'s a rickshaw strike near the main gate today. Plan extra travel time.'),
        ]

        for author, tag, title, body in posts_a:
            self._make_post(class_a, author, tag, title, body, a_members)
        for author, tag, title, body in posts_b:
            self._make_post(class_b, author, tag, title, body, b_members)

    def _make_post(self, classroom, author, tag, title, body, members):
        post = FeedPost.objects.create(classroom=classroom, author=author, tag=tag, title=title, body=body)
        voters = random.sample(members, k=min(len(members), random.randint(3, 6)))
        for voter in voters:
            FeedVote.objects.create(post=post, user=voter, value=random.choice([FeedVote.UP, FeedVote.UP, FeedVote.DOWN]))
        commenters = random.sample(members, k=min(len(members), random.randint(1, 3)))
        for commenter in commenters:
            if commenter.id == author.id:
                continue
            FeedComment.objects.create(post=post, author=commenter, text="Same here, following this thread.")

    # ---- summary ------------------------------------------------------

    def _print_summary(self, faculty_profiles, students):
        self.stdout.write(self.style.SUCCESS("\nDemo data seeded successfully.\n"))
        self.stdout.write(f"Shared password for every account: {PASSWORD}\n")
        self.stdout.write("Faculty logins:")
        for fp in faculty_profiles:
            self.stdout.write(f"  {fp.user.email}  ({fp.user.full_name}, {fp.get_designation_display()}, "
                               f"{'verified' if fp.is_verified else 'NOT verified'})")
        self.stdout.write("\nStudent logins:")
        for u in students:
            role = u.student_profile.get_user_type_display()
            self.stdout.write(f"  {u.email}  ({u.full_name}, {role})")
