import subprocess
from types import SimpleNamespace

from privip import network

IP_OUT = """2: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP
    inet 192.168.1.42/24 brd 192.168.1.255 scope global dynamic wlan0
"""


class FakeRun:
    def __init__(self, stdout="", returncode=0, stderr=""):
        self.calls = []
        self.result = SimpleNamespace(stdout=stdout, returncode=returncode, stderr=stderr)

    def __call__(self, cmd, **kw):
        self.calls.append(cmd)
        return self.result


def test_parse_ipv4():
    assert network.parse_ipv4(IP_OUT) == "192.168.1.42"
    assert network.parse_ipv4("") is None
    assert network.parse_ipv4("inet6 fe80::1/64") is None


def test_get_ipv4_calls_ip():
    run = FakeRun(IP_OUT)
    assert network.get_ipv4("wlan0", run=run) == "192.168.1.42"
    assert run.calls == [["ip", "-4", "addr", "show", "wlan0"]]


def test_read_mac(tmp_path):
    (tmp_path / "eth0").mkdir()
    (tmp_path / "eth0" / "address").write_text("aa:bb:cc:dd:ee:ff\n")
    assert network.read_mac("eth0", sys_net=str(tmp_path)) == "AA:BB:CC:DD:EE:FF"


def test_read_mac_missing_or_garbage(tmp_path):
    assert network.read_mac("nope", sys_net=str(tmp_path)) is None
    (tmp_path / "x").mkdir()
    (tmp_path / "x" / "address").write_text("garbage\n")
    assert network.read_mac("x", sys_net=str(tmp_path)) is None


def test_list_interfaces(tmp_path):
    for n in ("wlan0", "eth0"):
        (tmp_path / n).mkdir()
    assert network.list_interfaces(sys_net=str(tmp_path)) == ["eth0", "wlan0"]


def test_change_identity():
    run = FakeRun("ok", returncode=3, stderr="boom")
    assert network.change_identity("/bin/pc", "wlan0", run=run) == (3, "ok", "boom")
    assert run.calls == [["/bin/pc", "wlan0"]]


def test_service_unit():
    unit = network.service_unit("/v/python", "/repo")
    assert "ExecStart=/v/python -m privip.monitor" in unit
    assert "WorkingDirectory=/repo" in unit


def test_install_and_uninstall_service(tmp_path):
    path = tmp_path / "sub" / "svc.service"
    run = FakeRun()
    network.install_service("/py", "/repo", path=str(path), run=run)
    assert path.exists()
    assert [c[2] for c in run.calls] == ["daemon-reload", "enable", "start"]

    run = FakeRun()
    network.uninstall_service(path=str(path), run=run)
    assert not path.exists()
    assert [c[2] for c in run.calls] == ["stop", "disable"]


def test_is_service_active():
    assert network.is_service_active(run=FakeRun("active\n"))
    assert not network.is_service_active(run=FakeRun("inactive\n"))


def test_network_does_not_import_gui():
    import sys
    assert "customtkinter" not in sys.modules
