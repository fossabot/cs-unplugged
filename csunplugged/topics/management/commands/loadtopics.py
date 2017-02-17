from django.core.management.base import BaseCommand, CommandError
from topics.models import Topic, CurriculumLink, LearningOutcome
from django.utils.text import slugify
from django.db import transaction
import yaml
import os
import os.path
import sys
import markdown
import mdx_math
from kordac import Kordac

class Command(BaseCommand):
    help = 'Converts Markdown files listed in structure file and stores'

    def handle(self, *args, **options):
        """The function called when the loadtopics command is given"""

        # This path should be calculated, hardcoded for prototype
        self.BASE_PATH = 'topics/content/en/'
        self.converter = Kordac()
        language_structure = self.read_language_structure()

        # TODO: Think about how to store tag and HTML templates override for Kordac
        # Currently this needs to be called on each call to run() however
        # soon this will only be required on creation on Kordac converter
        self.tag_override = [
            'headingpre',
            'commentpre',
            'comment',
            'button',
            'video',
            'image',
        ]

        self.load_topics(language_structure)


    def read_language_structure(self):
        structure_file = open(os.path.join(self.BASE_PATH, 'structure.yml'), encoding='UTF-8')
        return yaml.load(structure_file.read())

    def print_load_log(self):
        for (log, indent) in self.load_log:
            self.stdout.write('{indent}{text}'.format(indent='  '*indent,text=log))
        self.stdout.write('\n')

    @transaction.atomic
    def load_topics(self, structure):
        self.load_log = []
        for topic_structure in structure['topics']:
            topic_data = self.convert_md_file(topic_structure['md-file'])

            other_resources_file = topic_structure['other-resources-md-file']
            if other_resources_file:
                other_resources_data = self.convert_md_file(other_resources_file)
                other_resources_html = other_resources_data.html_string
            else:
                other_resources_html = ''

            topic = Topic(
                slug=topic_structure['slug'],
                name=topic_data.heading,
                content=topic_data.html_string,
                other_resources=other_resources_html,
                icon=topic_structure['icon']
            )
            topic.save()
            self.load_log.append(('\nAdded Topic: {}'.format(topic.name), 0))

            # Load unit plans
            for unit_plan_structure_file in topic_structure['unit-plans']:
                self.load_unit_plan(unit_plan_structure_file, topic)

            # Load programming exercises
            if topic_structure['programming-exercises']:
                self.load_programming_exercises(topic_structure['programming-exercises'], topic)

            # Load follow up activities
            if topic_structure['follow-up-activities']:
                self.load_follow_up_activities(topic_structure['follow-up-activities'], topic)

        # Print log output
        self.print_load_log()

    def convert_md_file(self, file_path):
        """Returns the Kordac object for a given Markdown file"""
        content = open(os.path.join(self.BASE_PATH, file_path), encoding='UTF-8').read()
        return self.converter.run(content, tags=self.tag_override)


    def load_unit_plan(self, unit_plan_structure_file, topic):
        # TODO: Should create generic functions for loading YAML and reading file
        unit_plan_structure = yaml.load(open(os.path.join(self.BASE_PATH, unit_plan_structure_file), encoding='UTF-8').read())

        unit_plan_file = open(os.path.join(self.BASE_PATH, unit_plan_structure['md-file']), encoding='UTF-8')
        raw_content = unit_plan_file.read()
        unit_plan_content = self.converter.run(raw_content, tags=self.tag_override)

        unit_plan = topic.topic_unit_plans.create(
            slug=unit_plan_structure['slug'],
            name=unit_plan_content.heading,
            content=unit_plan_content.html_string,
        )
        unit_plan.save()
        self.load_log.append(('Added Unit Plan: {}'.format(unit_plan.name), 1))

        lessons_structure = unit_plan_structure['lessons']
        self.load_lessons(lessons_structure, topic, unit_plan)


    def load_lessons(self, lessons_structure, topic, unit_plan):
        for age_bracket, age_bracket_lessons in lessons_structure.items():
            for lesson_structure in age_bracket_lessons:
                self.load_lesson(lesson_structure, topic, unit_plan, age_bracket)


    def load_lesson(self, lesson_structure, topic, unit_plan, age_bracket):
        lesson_file = open(os.path.join(self.BASE_PATH, lesson_structure['md-file']), encoding='UTF-8')
        raw_content = lesson_file.read()
        lesson_content = self.converter.run(raw_content, tags=self.tag_override)

        lesson = topic.topic_lessons.create(
            unit_plan=unit_plan,
            slug=lesson_structure['slug'],
            name=lesson_content.heading,
            number=lesson_structure['lesson-number'],
            age_bracket=age_bracket,
            age_bracket_slug=slugify(age_bracket),
            content=lesson_content.html_string,
        )
        lesson.save()
        # Add learning outcomes
        for outcome in lesson_structure['learning-outcomes']:
            (object, created) = LearningOutcome.objects.get_or_create(
                text=outcome
            )
            lesson.learning_outcomes.add(object)
        # Add curriculum links
        for link in lesson_structure['curriculum-links']:
            (object, created) = CurriculumLink.objects.get_or_create(
                name=link
            )
            lesson.curriculum_links.add(object)
        self.load_log.append(('Added Lesson: {}'.format(lesson.__str__()), 2))


    def load_programming_exercises(self, programming_exercises_structure, topic):
        structure = yaml.load(open(os.path.join(self.BASE_PATH, programming_exercises_structure), encoding='UTF-8').read())

        for programming_exercise_data in structure:
            programming_exercise_content = self.convert_md_file(programming_exercise_data['md-file'])

            programming_exercise = topic.topic_programming_exercises.create(
                slug=programming_exercise_data['slug'],
                name=programming_exercise_content.heading,
                exercise_number=programming_exercise_data['exercise-number'],
                content=programming_exercise_content.html_string,
                scratch_hints=self.convert_md_file(programming_exercise_data['scratch']['hints']).html_string,
                scratch_solution=self.convert_md_file(programming_exercise_data['scratch']['solution']).html_string,
                python_hints=self.convert_md_file(programming_exercise_data['python']['hints']).html_string,
                python_solution=self.convert_md_file(programming_exercise_data['python']['solution']).html_string,
            )
            programming_exercise.save()

            for learning_outcome in programming_exercise_data['learning-outcomes']:
                (object, created) = LearningOutcome.objects.get_or_create(
                    text=learning_outcome
                )
                programming_exercise.learning_outcomes.add(object)
            self.load_log.append(('Added Programming Exercise: {}'.format(programming_exercise.name), 1))


    def load_follow_up_activities(self, follow_up_activities_structure, topic):
        if follow_up_activities_structure:
            structure = yaml.load(open(os.path.join(self.BASE_PATH, follow_up_activities_structure), encoding='UTF-8').read())

            for activity_data in structure:
                activity_file = open(os.path.join(self.BASE_PATH, activity_data['md-file']), encoding='UTF-8')
                raw_content = activity_file.read()
                activity_content = self.converter.run(raw_content, tags=self.tag_override)
                activity = topic.topic_follow_up_activities.create(
                    slug=activity_data['slug'],
                    name=activity_content.heading,
                    content=activity_content.html_string,
                )
                activity.save()
                for link in activity_data['curriculum-links']:
                    (object, created) = CurriculumLink.objects.get_or_create(
                        name=link
                    )
                    activity.curriculum_links.add(object)
                self.load_log.append(('Added Activity: {}'.format(activity.name), 1))


    def convert_md_file(self, filepath):
        file_object = open(os.path.join(self.BASE_PATH, filepath), encoding='UTF-8')
        raw_content = file_object.read()
        converted_file = self.converter.run(raw_content, tags=self.tag_override)
        return converted_file