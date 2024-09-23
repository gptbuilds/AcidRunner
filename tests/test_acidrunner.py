import pytest
from acidrunner.acid_runner import AcidRunner
from io import StringIO

# Mock YAML content that will be written to the file in both tests
yaml_content = """
systems_under_test:
  - name: security-filter
    entrypoint_benchmarks: demos/security-filter/benches.py
    entrypoint_tests: demos/security/tests.py
    tracemalloc_enabled: true

buckets:
  - name: bucket_groq
    rpm: 30
  - name: bucket_openai
    rpm: 500
  - name: bucket_custom_fast
    rpm: 100000
  - name: bucket_custom_slow
    rpm: 10

file_settings:
  - data_dir: /home/user/dev/py/groq
"""

@pytest.fixture
def mock_yaml_data():
    """Mock YAML configuration for the AcidRunner settings."""
    return yaml_content

@pytest.fixture
def write_yaml_to_file(tmp_path):
    """Write the mock YAML content to a temporary file."""
    yaml_file = tmp_path / "settings.yaml"
    yaml_file.write_text(yaml_content)
    return yaml_file

def test_acidrunner_load_settings_mock(mock_yaml_data, monkeypatch):
    """Test the AcidRunner's ability to load and parse YAML settings."""
    
    # Mock open() to return the mock YAML data instead of reading a file
    def mock_open(*args, **kwargs):
        return StringIO(mock_yaml_data)

    # Use monkeypatch to substitute the open function within the context of this test
    monkeypatch.setattr("builtins.open", mock_open)

    # Initialize AcidRunner with any file path since open() is mocked
    runner = AcidRunner("mock_config.yaml")
    settings = runner.load_settings()

    # Assertions to check if settings were loaded correctly
    assert settings.systems_under_test[0]['name'] == 'security-filter'
    assert settings.buckets[0]['name'] == 'bucket_groq'
    assert settings.buckets[0]['rpm'] == 30
    assert settings.file_settings[0]['data_dir'] == '/home/user/dev/py/groq'

def test_acidrunner_load_settings_from_file(write_yaml_to_file):
    """Test the AcidRunner's ability to load YAML settings directly from an actual file."""
    
    # Initialize AcidRunner with the actual file path
    runner = AcidRunner(str(write_yaml_to_file))
    settings = runner.load_settings()

    # Assertions to check if settings were loaded correctly
    assert settings.systems_under_test[0]['name'] == 'security-filter'
    assert settings.buckets[0]['name'] == 'bucket_groq'
    assert settings.buckets[0]['rpm'] == 30
    assert settings.file_settings[0]['data_dir'] == '/home/user/dev/py/groq'
