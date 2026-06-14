"""The text-to-SQL static guard is security-critical — test it hard."""
import pytest

from vayu.nlsql import guard_sql


def test_allows_plain_select_and_forces_limit():
    out = guard_sql("select accepted_name from plant")
    assert out.lower().startswith("select")
    assert "limit" in out.lower()


def test_allows_cte():
    out = guard_sql("with t as (select 1 as n) select n from t limit 5")
    assert out.lower().startswith("with")


def test_preserves_existing_limit():
    out = guard_sql("select 1 limit 7")
    assert out.lower().count("limit") == 1
    assert out.strip().endswith("7")


@pytest.mark.parametrize(
    "bad",
    [
        "delete from plant",
        "update plant set family = 'x'",
        "drop table plant",
        "truncate plant",
        "insert into plant(accepted_name) values ('x')",
        "grant select on plant to public",
        "select 1; drop table plant",          # stacked statement
        "select * from plant into outfile '/tmp/x'",
    ],
)
def test_rejects_writes_and_ddl(bad):
    with pytest.raises(ValueError):
        guard_sql(bad)


def test_rejects_non_select():
    with pytest.raises(ValueError):
        guard_sql("explain analyze select 1")


def test_no_false_positive_on_domain_terms():
    # 'dosha_effect' must not trip the \bdo\b rule; 'plant_use' must not trip anything.
    out = guard_sql("select value from property_term where kind = 'dosha_effect' limit 5")
    assert "limit" in out.lower()
