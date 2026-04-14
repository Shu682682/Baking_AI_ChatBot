from app.chat_service import extract_servings


def test_extract_servings():
    assert extract_servings("I want to make 20 servings chocolate cake", 8) == 20
    assert extract_servings("for 12 people", 8) == 12
    assert extract_servings("serves 6", 8) == 6
    assert extract_servings("chocolate cake", 8) == 8


def test_extract_servings_chinese_people():
    assert extract_servings("我要做南瓜派5個人", 8) == 5


def test_extract_servings_chinese_servings():
    assert extract_servings("我要做10人份巧克力蛋糕", 8) == 10


def test_extract_servings_for_people():
    assert extract_servings("I want pumpkin pie for 6 people", 8) == 6


def test_extract_servings_make_people():
    assert extract_servings("I want to make 10 people strawberry cake", 8) == 10


def test_extract_servings_servings_word():
    assert extract_servings("Give me a brownie recipe for 12 servings", 8) == 12


def test_extract_servings_default_when_missing():
    assert extract_servings("I want tiramisu", 8) == 8