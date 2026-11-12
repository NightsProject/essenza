from jinja2 import Environment, FileSystemLoader


TEMPLATE_DIR = "app/templates"


def test_methodology_describes_experiment_and_evaluation_scope():
    template = Environment(loader=FileSystemLoader(TEMPLATE_DIR)).get_template("methodology.html")
    template.environment.globals["url_for"] = lambda *args, **kwargs: "/static/mock"
    rendered = template.render()

    assert "540 training sources" in rendered
    assert "110 validation sources" in rendered
    assert "50 held-out test sources" in rendered
    assert "paired bootstrap" in rendered.lower()
    assert "ROUGE-L" in rendered
    assert "interactive generation" in rendered.lower()
    assert "does not reproduce the full held-out research evaluation" in rendered.lower()
