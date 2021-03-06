# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# inspirehep is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

import json

from helpers.providers.faker import faker

from inspirehep.records.marshmallow.authors import AuthorsDetailSchema


def test_should_display_positions_without_positions():
    schema = AuthorsDetailSchema()
    data = {
        "name": {"value": "Doe, John", "preferred_name": "J Doe"},
        "ids": [{"schema": "INSPIRE BAI", "value": "John.Doe.1"}],
    }
    author = faker.record("aut", data=data, with_control_number=True)

    expected_result = False

    result = schema.dumps(author).data
    result_data = json.loads(result)
    result_should_display_positions = result_data.get("should_display_positions")

    assert expected_result == result_should_display_positions


def test_should_display_positions_with_multiple_positions():
    schema = AuthorsDetailSchema()
    data = {
        "name": {"value": "Doe, John", "preferred_name": "J Doe"},
        "ids": [{"schema": "INSPIRE BAI", "value": "John.Doe.1"}],
        "positions": [{"institution": "CERN"}, {"institution": "DESY"}],
    }
    author = faker.record("aut", data=data, with_control_number=True)

    expected_result = True

    result = schema.dumps(author).data
    result_data = json.loads(result)
    result_should_display_positions = result_data.get("should_display_positions")

    assert expected_result == result_should_display_positions


def test_should_display_positions_with_multiple_positions_with_rank():
    schema = AuthorsDetailSchema()
    data = {
        "name": {"value": "Doe, John", "preferred_name": "J Doe"},
        "ids": [{"schema": "INSPIRE BAI", "value": "John.Doe.1"}],
        "positions": [{"institution": "CERN", "rank": "PHD", "current": True}],
    }
    author = faker.record("aut", data=data, with_control_number=True)

    expected_result = True

    result = schema.dumps(author).data
    result_data = json.loads(result)
    result_should_display_positions = result_data.get("should_display_positions")

    assert expected_result == result_should_display_positions


def test_should_display_positions_with_multiple_positions_with_start_date():
    schema = AuthorsDetailSchema()
    data = {
        "name": {"value": "Doe, John", "preferred_name": "J Doe"},
        "ids": [{"schema": "INSPIRE BAI", "value": "John.Doe.1"}],
        "positions": [{"institution": "CERN", "start_date": "2015", "current": True}],
    }
    author = faker.record("aut", data=data, with_control_number=True)

    expected_result = True

    result = schema.dumps(author).data
    result_data = json.loads(result)
    result_should_display_positions = result_data.get("should_display_positions")

    assert expected_result == result_should_display_positions


def test_should_display_positions_with_multiple_positions_if_is_not_current():
    schema = AuthorsDetailSchema()
    data = {
        "name": {"value": "Doe, John", "preferred_name": "J Doe"},
        "ids": [{"schema": "INSPIRE BAI", "value": "John.Doe.1"}],
        "positions": [{"institution": "CERN", "current": False}],
    }
    author = faker.record("aut", data=data, with_control_number=True)

    expected_result = True

    result = schema.dumps(author).data
    result_data = json.loads(result)
    result_should_display_positions = result_data.get("should_display_positions")

    assert expected_result == result_should_display_positions


def test_returns_should_display_position_false_if_position_is_current():
    schema = AuthorsDetailSchema()
    data = {
        "name": {"value": "Doe, John", "preferred_name": "J Doe"},
        "ids": [{"schema": "INSPIRE BAI", "value": "John.Doe.1"}],
        "positions": [{"institution": "CERN", "current": True}],
    }
    author = faker.record("aut", data=data, with_control_number=True)

    expected_result = False

    result = schema.dumps(author).data
    result_data = json.loads(result)
    result_should_display_positions = result_data.get("should_display_positions")

    assert expected_result == result_should_display_positions


def test_facet_author_name_with_preferred_name_and_control_number():
    schema = AuthorsDetailSchema()
    data = {
        "name": {"value": "Doe, John", "preferred_name": "J Doe"},
        "control_number": 1,
    }
    author = faker.record("aut", data=data)

    expected_result = "1_J Doe"

    result = schema.dumps(author).data
    result_data = json.loads(result)
    result_facet_author_name = result_data.get("facet_author_name")

    assert expected_result == result_facet_author_name


def test_facet_author_name_without_preferred_name():
    schema = AuthorsDetailSchema()
    data = {"name": {"value": "Doe, John"}, "control_number": 1}
    author = faker.record("aut", data=data)

    expected_result = "1_John Doe"

    result = schema.dumps(author).data
    result_data = json.loads(result)
    result_facet_author_name = result_data.get("facet_author_name")

    assert expected_result == result_facet_author_name


def test_author_twitter():
    schema = AuthorsDetailSchema()
    data = {"ids": [{"value": "harunurhan", "schema": "TWITTER"}]}
    author = faker.record("aut", data=data, with_control_number=True)
    expected_twitter = "harunurhan"

    result = schema.dumps(author).data
    result_data = json.loads(result)
    result_twitter = result_data.get("twitter")

    assert expected_twitter == result_twitter


def test_author_linkedin():
    schema = AuthorsDetailSchema()
    data = {"ids": [{"value": "harunurhan", "schema": "LINKEDIN"}]}
    author = faker.record("aut", data=data, with_control_number=True)
    expected_linkedin = "harunurhan"

    result = schema.dumps(author).data
    result_data = json.loads(result)
    result_linkedin = result_data.get("linkedin")

    assert expected_linkedin == result_linkedin


def test_author_does_not_have_id_fields():
    schema = AuthorsDetailSchema()
    author = faker.record("aut", with_control_number=True)

    result = schema.dumps(author).data
    result_data = json.loads(result)

    assert "linkedin" not in result_data
    assert "twitter" not in result_data
    assert "orcid" not in result_data
    assert "bai" not in result_data


def test_author_bai():
    schema = AuthorsDetailSchema()
    data = {"ids": [{"schema": "INSPIRE BAI", "value": "John.Doe.1"}]}
    author = faker.record("aut", data=data, with_control_number=True)
    expected_bai = "John.Doe.1"

    result = schema.dumps(author).data
    result_data = json.loads(result)
    result_bai = result_data.get("bai")

    assert expected_bai == result_bai


def test_author_orcid():
    schema = AuthorsDetailSchema()
    data = {"ids": [{"value": "0000-0001-8058-0014", "schema": "ORCID"}]}
    author = faker.record("aut", data=data, with_control_number=True)
    expected_orcid = "0000-0001-8058-0014"

    result = schema.dumps(author).data
    result_data = json.loads(result)
    result_orcid = result_data.get("orcid")

    assert expected_orcid == result_orcid


def test_only_public_and_current_emails():
    schema = AuthorsDetailSchema()
    data = {
        "email_addresses": [
            {"value": "current-private@mail.cern", "current": True, "hidden": True},
            {"value": "current-public@mail.cern", "current": True, "hidden": False},
            {"value": "outdated-public@mail.cern", "current": False, "hidden": False},
            {"value": "outdated-private@mail.cern", "current": False, "hidden": True},
        ]
    }
    author = faker.record("aut", data=data, with_control_number=True)
    expected_email_addresses = [
        {"value": "current-public@mail.cern", "current": True, "hidden": False}
    ]

    result = schema.dumps(author).data
    result_data = json.loads(result)
    result_email_addresses = result_data.get("email_addresses")

    assert expected_email_addresses == result_email_addresses
