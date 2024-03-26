from src.skippy.utils import load_config_file


def test_load_config_file():
    config = load_config_file()
    assert config == {
        "repositories":[
            {"55736342": "pytest"}
        ]
    }