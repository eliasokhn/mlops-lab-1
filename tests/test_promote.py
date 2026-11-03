from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.food11.promote import promote


@pytest.mark.parametrize("accuracy,expected", [(0.90, "champion"), (0.81, "challenger")])
def test_gate(accuracy, expected):
    client = Mock()
    client.get_model_version.return_value = SimpleNamespace(version="2", run_id="candidate")
    client.get_model_version_by_alias.return_value = SimpleNamespace(version="1", run_id="old")
    client.get_run.side_effect = lambda run: SimpleNamespace(
        data=SimpleNamespace(metrics={"test_accuracy": accuracy if run == "candidate" else 0.80}))
    assert promote(client, "food11", "2", 1000) == expected
    client.set_registered_model_alias.assert_called_once_with("food11", expected, "2")
    assert client.set_model_version_tag.call_count == 6
