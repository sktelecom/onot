import onot


def test_version():
    assert onot.__version__.startswith("2.")
